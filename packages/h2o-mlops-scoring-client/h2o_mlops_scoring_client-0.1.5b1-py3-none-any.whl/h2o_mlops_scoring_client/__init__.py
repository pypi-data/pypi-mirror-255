import datetime as _datetime
import logging as _logging
import os as _os
import pathlib as _pathlib
import typing as _typing
from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor
from multiprocessing import cpu_count as _cpu_count

import numpy as _numpy
import pandas as _pandas
import pyspark as _pyspark

from h2o_mlops_scoring_client import _utils
from h2o_mlops_scoring_client._configs import FeatureType
from h2o_mlops_scoring_client._configs import Format
from h2o_mlops_scoring_client._configs import WriteMode
from h2o_mlops_scoring_client._version import version as __version__  # noqa: F401


_logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%y/%m/%d %H:%M:%S",
    level=_logging.INFO,
)
logger = _logging.getLogger(__name__)
spark_conf_dir = _os.environ.get("SPARK_CONF_DIR")
spark_master = _utils.get_spark_master()


def get_capabilities(
    mlops_endpoint_url: str, passphrase: _typing.Optional[str] = None
) -> _typing.List[str]:
    """Capabilities of the scoring endpoint.

    Args:
        mlops_endpoint_url: MLOps deployment scoring endpoint URL
        passphrase: passphrase for protected MLOps endpoint
    """
    return _utils.MLOpsEndpoint(mlops_endpoint_url, passphrase).capabilities


def get_experiment_id(
    mlops_endpoint_url: str, passphrase: _typing.Optional[str] = None
) -> str:
    """ID of experiment used for scoring by the scoring endpoint.

    Args:
        mlops_endpoint_url: MLOps deployment scoring endpoint URL
        passphrase: passphrase for protected MLOps endpoint
    """
    return _utils.MLOpsEndpoint(mlops_endpoint_url, passphrase).experiment_id


def get_schema(
    mlops_endpoint_url: str, passphrase: _typing.Optional[str] = None
) -> _typing.Dict[str, _typing.Any]:
    """Column names and types expected by the scoring endpoint.

    Args:
        mlops_endpoint_url: MLOps deployment scoring endpoint URL
        passphrase: passphrase for protected MLOps endpoints
    """
    return _utils.MLOpsEndpoint(mlops_endpoint_url, passphrase).schema


def get_spark_session(
    app_name: str = "h2o_mlops_scoring_client",
    mini_batch_size: int = 1000,
    spark_config_overrides: _typing.Optional[_typing.Dict[str, str]] = None,
) -> _pyspark.sql.SparkSession:
    """Get or create a Spark session configured for the scoring client.

    Args:
        app_name: name of application in Spark
        mini_batch_size: number of rows per scorer call
        spark_config_overrides: pass Spark configuration options to the Spark context
    """
    if spark_master.startswith("local"):
        # quiet spark warnings
        import importlib.resources

        try:
            resource = importlib.resources.files(  # type: ignore
                "h2o_mlops_scoring_client"
            ).joinpath("log4j.properties")
        except AttributeError:
            # fallback for Python < 3.9
            with importlib.resources.path(
                "h2o_mlops_scoring_client", "log4j.properties"
            ) as resource:
                pass
        _os.environ["LOG4J_CONFIGURATION_FILE"] = str(resource)
        # ignore local SPARK_HOME
        _os.environ.pop("SPARK_HOME", None)

    if spark_master.startswith("local") and spark_conf_dir:
        if not _pathlib.Path(spark_conf_dir, "spark-defaults.conf").is_file():
            logger.warning(
                f"SPARK_CONF_DIR is set to '{spark_conf_dir}' "
                f"but 'spark-defaults.conf' was not found."
            )
        _os.environ["SPARK_CONF_DIR"] = _os.path.abspath(spark_conf_dir)

    return _utils.get_spark_session(
        app_name=app_name,
        master=spark_master,
        mini_batch_size=mini_batch_size,
        spark_config=spark_config_overrides,
    )


def score_source_sink(
    *,
    mlops_endpoint_url: str,
    id_column: str,
    source_data: str,
    source_format: Format,
    sink_location: str,
    sink_format: Format,
    sink_write_mode: WriteMode,
    passphrase: _typing.Optional[str] = None,
    request_contributions: _typing.Optional[FeatureType] = None,
    source_config: _typing.Optional[_typing.Dict[str, str]] = None,
    sink_config: _typing.Optional[_typing.Dict[str, str]] = None,
    preprocess_method: _typing.Optional[_typing.Callable] = None,
    postprocess_method: _typing.Optional[_typing.Callable] = None,
    mini_batch_size: int = 1000,
    spark_config_overrides: _typing.Optional[_typing.Dict[str, str]] = None,
) -> None:
    """Use Spark to do parallelized scoring in mini-batches against a MLOps deployment.

    Args:
        mlops_endpoint_url: MLOps deployment scoring endpoint URL
        id_column: name of column in data to be scored
            - column should contain unique row identifiers
        source_data: path or query for data to be scored
        source_format: file type or table type data to be scored is stored in
        sink_location: path or query for scored data to be written to
        sink_format: file type or table type for scored data when written
        sink_write_mode: write behavior when data already exists in sink location
        passphrase: passphrase for protected MLOps endpoint
        request_contributions: if supported by the model, include the contributions
            in the output for the specified feature type
        source_config: pass Spark data source options for the specified format
            (useful for JDBC_QUERY and JDBC_TABLE formats)
        sink_config: pass Spark data source options for the specified format
            (useful for JDBC_QUERY and JDBC_TABLE formats)
        preprocess_method: method that takes and returns a Spark dataframe
            before scoring
        postprocess_method: method that takes and returns a Spark dataframe
            after scoring
        mini_batch_size: number of rows per scorer call
        spark_config_overrides: pass Spark configuration options to the Spark context
    """
    try:
        start = _datetime.datetime.now().replace(microsecond=0)

        spark = get_spark_session(
            mini_batch_size=mini_batch_size,
            spark_config_overrides=spark_config_overrides,
        )

        logger.info(f"Connecting to H2O.ai MLOps scorer at '{mlops_endpoint_url}'")
        mlops_endpoint = _utils.MLOpsEndpoint(mlops_endpoint_url, passphrase)

        sdf = _utils.read_source(spark, source_data, source_format, source_config)

        if preprocess_method:
            logger.info("Applying preprocess method")
            sdf = preprocess_method(sdf)

        logger.info(f"Starting scoring from '{source_data}' to '{sink_location}'")
        start_scoring = _datetime.datetime.now().replace(microsecond=0)
        scored_sdf = mlops_endpoint.score_spark_dataframe(
            sdf, id_column=id_column, request_contributions=request_contributions
        )

        if postprocess_method:
            logger.info("Applying postprocess method")
            scored_sdf = postprocess_method(scored_sdf)

        _utils.write_sink(
            scored_sdf, sink_location, sink_format, sink_write_mode, sink_config
        )

        logger.info("Scoring complete")
        stop = _datetime.datetime.now().replace(microsecond=0)

        logger.info(f"Total run time: {stop - start}")
        logger.info(f"Scoring run time: {stop - start_scoring}")

    finally:
        if spark_master.startswith("local"):
            try:
                spark.stop()
            except UnboundLocalError:
                pass


def score_data_frame(
    *,
    mlops_endpoint_url: str,
    id_column: str,
    data_frame: _typing.Union[_pandas.DataFrame, _pyspark.sql.DataFrame],
    mini_batch_size: int = 1000,
    passphrase: _typing.Optional[str] = None,
    request_contributions: _typing.Optional[FeatureType] = None,
    spark_config_overrides: _typing.Optional[_typing.Dict[str, str]] = None,
) -> _typing.Union[_pandas.DataFrame, _pyspark.sql.DataFrame]:
    """Do scoring of a Pandas or Spark data frame against a MLOps deployment.

    Args:
        mlops_endpoint_url: MLOps deployment scoring endpoint URL
        id_column: name of column in data to be scored
            - column should contain unique row identifiers
        data_frame: Pandas or Spark data frame
        mini_batch_size: number of rows per scorer call
        passphrase: passphrase for protected MLOps endpoint
        request_contributions: if supported by the model, include the contributions
            in the output for the specified feature type
        spark_config_overrides: pass Spark configuration options to the Spark context
    """
    if isinstance(data_frame, _pandas.DataFrame):
        return _score_data_frame_pandas(
            mlops_endpoint_url=mlops_endpoint_url,
            passphrase=passphrase,
            id_column=id_column,
            request_contributions=request_contributions,
            data_frame=data_frame,
            mini_batch_size=mini_batch_size,
        )
    else:
        return _score_data_frame_spark(
            mlops_endpoint_url=mlops_endpoint_url,
            passphrase=passphrase,
            id_column=id_column,
            request_contributions=request_contributions,
            data_frame=data_frame,
            mini_batch_size=mini_batch_size,
            spark_config_overrides=spark_config_overrides,
        )


def _score_data_frame_pandas(
    *,
    mlops_endpoint_url: str,
    id_column: str,
    data_frame: _pandas.DataFrame,
    mini_batch_size: int = 1000,
    passphrase: _typing.Optional[str] = None,
    request_contributions: _typing.Optional[FeatureType] = None,
) -> _pandas.DataFrame:
    start = _datetime.datetime.now().replace(microsecond=0)
    num_partitions = int(_numpy.ceil(len(data_frame) / mini_batch_size))
    max_cpu_count = 4
    max_workers = min(_cpu_count() // 2, max_cpu_count)
    max_workers = min(max_workers, num_partitions)

    logger.info(f"Connecting to H2O.ai MLOps scorer at '{mlops_endpoint_url}'")
    mlops_endpoint = _utils.MLOpsEndpoint(mlops_endpoint_url, passphrase)
    input_columns = [id_column] + [
        f["name"] for f in mlops_endpoint.schema["inputFields"]
    ]

    logger.info("Starting scoring data frame")
    start_scoring = _datetime.datetime.now().replace(microsecond=0)
    with _ThreadPoolExecutor(max_workers=max_workers) as executor:
        mini_batches = (
            data_frame[input_columns].iloc[i : i + mini_batch_size]  # noqa: E203
            for i in range(0, len(data_frame), mini_batch_size)
        )
        results = [
            executor.submit(
                mlops_endpoint.score_pandas_dataframe,
                pdf=mini_batch,
                id_column=id_column,
                request_contributions=request_contributions,
            )
            for mini_batch in mini_batches
        ]
        scored_df = _pandas.concat(
            (result.result() for result in results), ignore_index=True
        )

    logger.info("Scoring complete")
    stop = _datetime.datetime.now().replace(microsecond=0)

    logger.info(f"Total run time: {stop - start}")
    logger.info(f"Scoring run time: {stop - start_scoring}")

    return scored_df


def _score_data_frame_spark(
    *,
    mlops_endpoint_url: str,
    id_column: str,
    data_frame: _pyspark.sql.DataFrame,
    mini_batch_size: int = 1000,
    passphrase: _typing.Optional[str] = None,
    request_contributions: _typing.Optional[FeatureType] = None,
    spark_config_overrides: _typing.Optional[_typing.Dict[str, str]] = None,
) -> _typing.Union[_pandas.DataFrame, _pyspark.sql.DataFrame]:
    get_spark_session(
        mini_batch_size=mini_batch_size,
        spark_config_overrides=spark_config_overrides,
    )

    logger.info(f"Connecting to H2O.ai MLOps scorer at '{mlops_endpoint_url}'")
    mlops_endpoint = _utils.MLOpsEndpoint(mlops_endpoint_url, passphrase)

    scored_df = mlops_endpoint.score_spark_dataframe(
        data_frame, id_column=id_column, request_contributions=request_contributions
    )

    return scored_df
