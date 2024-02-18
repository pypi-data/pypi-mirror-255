import copy as _copy
import logging as _logging
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Iterator as _Iterator
from typing import List as _List
from typing import Optional as _Optional

import pandas as _pandas
import pyspark as _pyspark
import pyspark.sql as _pyspark_sql
import pyspark.sql.types as _pyspark_sql_types
import requests as _requests
from requests.adapters import HTTPAdapter as _HTTPAdapter
from urllib3.util import Retry as _Retry

from h2o_mlops_scoring_client import _configs


logger = _logging.getLogger(__name__)


class MLOpsEndpoint:
    """Python wrapper giving convenient access to H2O.ai MLOps endpoint
    information and scoring.
    """

    def __init__(self, url: str, passphrase: _Optional[str] = None):
        url = url.rstrip("/")
        if url.endswith("model"):
            self._endpoint_parent_url = url
        else:
            self._endpoint_parent_url = "/".join(url.split("/")[:-1])
        self._capabilities_url = f"{self._endpoint_parent_url}/capabilities"
        self._experiment_id_url = f"{self._endpoint_parent_url}/id"
        self._sample_request_url = f"{self._endpoint_parent_url}/sample_request"
        self._schema_url = f"{self._endpoint_parent_url}/schema"
        self._score_url = f"{self._endpoint_parent_url}/score"

        self._capabilities = None
        self._experiment_id: _Optional[str] = None
        self._sample_request = None
        self._schema = None

        session_retry = _Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[403, 404],
        )
        adapter = _HTTPAdapter(max_retries=session_retry)
        self._session = _requests.Session()
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        if passphrase is not None:
            self._session.headers = {"Authorization": f"Bearer {passphrase}"}

        # for post to score url
        session_retry = _Retry(
            total=10,
            status_forcelist=[404, 502, 503, 504],
            backoff_factor=0.2,
            allowed_methods=["POST"],
        )
        adapter = _HTTPAdapter(max_retries=session_retry)
        self._score_session = _requests.Session()
        self._score_session.mount(self.score_url, adapter)
        if passphrase is not None:
            self._score_session.headers = {"Authorization": f"Bearer {passphrase}"}

        self._spark_type_map = {
            "bool": _pyspark_sql_types.BooleanType(),
            "int32": _pyspark_sql_types.IntegerType(),
            "int64": _pyspark_sql_types.LongType(),
            "float32": _pyspark_sql_types.FloatType(),
            "float64": _pyspark_sql_types.DoubleType(),
            "str": _pyspark_sql_types.StringType(),
            "time64": _pyspark_sql_types.TimestampType(),
        }

        # check if endpoint url is valid
        try:
            self.capabilities
        except _requests.exceptions.RetryError as e:
            print(f"Can't connect to endpoint, is the URL {url} correct?")
            raise e

    @property
    def capabilities(self) -> _List[str]:
        """Endpoint's capabilities converted to a Python list."""
        if not self._capabilities:
            r = self._session.get(self.capabilities_url)
            r.raise_for_status()
            self._capabilities = r.json()
        return self._capabilities

    @property
    def capabilities_url(self) -> str:
        """URL for retrieving endpoint's capabilities with GET method."""
        return self._capabilities_url

    @property
    def experiment_id(self) -> str:
        """Endpoint's experiment ID."""
        if not self._experiment_id:
            r = self._session.get(self._experiment_id_url)
            r.raise_for_status()
            self._experiment_id = r.text
        return self._experiment_id

    @property
    def experiment_id_url(self) -> str:
        """URL for retrieving endpoint's experiment ID with GET method."""
        return self._experiment_id_url

    @property
    def sample_request(self) -> _Dict[str, _Any]:
        """Endpoint's sample_request JSON converted to a Python dictionary."""
        if not self._sample_request:
            r = self._session.get(self.sample_request_url)
            r.raise_for_status()
            self._sample_request = r.json()
        return self._sample_request

    @property
    def sample_request_url(self) -> str:
        """URL for retrieving endpoint's sample_request with GET method."""
        return self._sample_request_url

    @property
    def schema(self) -> _Dict[str, _Any]:
        """Endpoint's full schema JSON converted to a Python dictionary."""
        if not self._schema:
            r = self._session.get(self.schema_url)
            r.raise_for_status()
            schema = r.json()["schema"]
            # work around for mlops reporting prediction intervals when none exist
            if any(
                f["name"].endswith(".lower") for f in schema["outputFields"]
            ) and any(f["name"].endswith(".upper") for f in schema["outputFields"]):
                try:
                    schema["outputFields"] = [
                        f
                        for f in schema["outputFields"]
                        if f["name"] in self._get_prediction_columns()
                    ]
                except _requests.exceptions.HTTPError:
                    logger.warning("Could not confirm prediction column names.")
            self._schema = schema
        return self._schema

    @property
    def schema_spark_input(self) -> _pyspark_sql_types.StructType:
        """Endpoint's input schema JSON converted to a PySpark schema object."""
        fields = [
            _pyspark_sql_types.StructField(
                name=c["name"], dataType=self._spark_type_map[c["dataType"].lower()]
            )
            for c in self.schema["inputFields"]
        ]
        return _pyspark_sql_types.StructType(fields)

    @property
    def schema_spark_output(self) -> _pyspark_sql_types.StructType:
        """Endpoint's output schema JSON converted to a PySpark schema object."""
        fields = [
            _pyspark_sql_types.StructField(
                name=c["name"], dataType=self._spark_type_map[c["dataType"].lower()]
            )
            for c in self.schema["outputFields"]
        ]
        return _pyspark_sql_types.StructType(fields)

    @property
    def schema_url(self) -> str:
        """URL for retrieving endpoint's schema with GET method."""
        return self._schema_url

    @property
    def score_url(self) -> str:
        """URL for endpoint scoring with POST method."""
        return self._score_url

    def _check_contribution_capabilities(
        self, feature_type: _configs.FeatureType
    ) -> None:
        """Raise error if contributions not available for feature type."""
        if (
            feature_type == _configs.FeatureType.ORIGINAL
            and "CONTRIBUTION_ORIGINAL" in self.capabilities
        ):
            return
        elif (
            feature_type == _configs.FeatureType.TRANSFORMED
            and "CONTRIBUTION_TRANSFORMED" in self.capabilities
        ):
            return
        else:
            raise RuntimeError(
                "MLOps deployment does not support contributions for feature "
                f"type: {feature_type}"
            )

    def _get_prediction_columns(self) -> _List[str]:
        empty_request = self.sample_request
        empty_request["rows"] = []
        response = self._score_session.post(url=self.score_url, json=empty_request)
        response.raise_for_status()
        return response.json()["fields"]

    def schema_spark_output_w_contribs(
        self, request_contributions: _Optional[_configs.FeatureType] = None
    ) -> _pyspark_sql_types.StructType:
        """Endpoint's output schema JSON and contribution fields converted to
        a PySpark schema object.
        """
        fields = [
            _pyspark_sql_types.StructField(
                name=c["name"], dataType=self._spark_type_map[c["dataType"].lower()]
            )
            for c in self.schema["outputFields"]
        ]
        if request_contributions:
            empty_request = self.sample_request
            empty_request["requestShapleyValueType"] = request_contributions.value
            empty_request["rows"] = []
            features = self._score_session.post(
                url=self.score_url, json=empty_request
            ).json()["featureShapleyContributions"]["features"]
            fields.extend(
                [
                    _pyspark_sql_types.StructField(
                        name=c,
                        dataType=_pyspark_sql_types.FloatType(),
                    )
                    for c in features
                ]
            )
        return _pyspark_sql_types.StructType(fields)

    def score_pandas_dataframe(
        self,
        pdf: _pandas.DataFrame,
        id_column: _Optional[str] = None,
        request_contributions: _Optional[_configs.FeatureType] = None,
    ) -> _pandas.DataFrame:
        """Score a Pandas DataFrame as long as the size does not exceed the
        maximum request size of the endpoint.
        """
        dtypes = pdf.dtypes.to_dict()
        for k, v in dtypes.items():
            if str(v).startswith("Int"):
                dtypes[k] = float
        payload = dict(
            fields=list(pdf.columns),
            rows=pdf.astype(dtypes).fillna("").astype(str).to_dict("split")["data"],
        )
        if request_contributions:
            self._check_contribution_capabilities(request_contributions)
            payload["requestShapleyValueType"] = request_contributions.value
        result = self._score_session.post(url=self.score_url, json=payload, timeout=60)
        result.raise_for_status()
        result_dataframe = _pandas.DataFrame(
            data=result.json()["score"], columns=result.json()["fields"]
        ).astype(float, errors="ignore")
        if id_column:
            result_dataframe[id_column] = pdf[id_column].values
        # need to filter fields as schema sometimes doesn't include bounds for
        # regression intervals
        output_columns = []
        if id_column:
            output_columns.append(id_column)
        output_columns.extend(
            [c["name"] for c in self.schema["outputFields"] if c["name"]]
        )
        result_dataframe = result_dataframe[output_columns]
        if request_contributions:
            contrib_dataframe = _pandas.DataFrame(
                data=result.json()["featureShapleyContributions"]["contributionGroups"][
                    0
                ]["contributions"],
                columns=result.json()["featureShapleyContributions"]["features"],
            ).astype(float, errors="ignore")
            result_dataframe = _pandas.concat(
                [result_dataframe, contrib_dataframe], axis=1
            )
        return result_dataframe

    def score_spark_dataframe(
        self,
        sdf: _pyspark_sql.DataFrame,
        id_column: str,
        request_contributions: _Optional[_configs.FeatureType] = None,
    ) -> _pyspark_sql.DataFrame:
        """Score a Spark DataFrame of any size in mini-batches (requires Spark 3).

        Batch size is determined by the Spark config
        "spark.sql.execution.arrow.maxRecordsPerBatch".
        Larger mini-batch sizes can process quicker but may exceed the maximum
        request size of the endpoint. Recommended starting mini-batch size is 1000.
        """

        if request_contributions:
            self._check_contribution_capabilities(request_contributions)

        def score_pandas_dataframe_spark(
            iterator: _Iterator[_pandas.DataFrame],
        ) -> _Iterator[_pandas.DataFrame]:
            for pdf in iterator:
                yield self.score_pandas_dataframe(
                    pdf=pdf,
                    id_column=id_column,
                    request_contributions=request_contributions,
                )

        if id_column in self.schema_spark_input.fieldNames():
            input_schema = _pyspark_sql_types.StructType(
                [f for f in self.schema_spark_input]
            )
        else:
            id_column_schema = sdf.schema[id_column]
            if isinstance(id_column_schema.dataType, _pyspark_sql_types.DecimalType):
                id_column_schema.dataType = _pyspark_sql_types.FloatType()
            input_schema = _pyspark_sql_types.StructType(
                [id_column_schema] + [f for f in self.schema_spark_input]
            )
        output_schema = _pyspark_sql_types.StructType(
            [id_column_schema]
            + [
                f
                for f in self.schema_spark_output_w_contribs(
                    request_contributions=request_contributions
                )
            ]
        )
        sdf = sdf.select(
            *[
                sdf[f"{column.name}"].cast(f"{column.dataType.typeName()}")
                for column in input_schema
            ]
        )
        scores = sdf.mapInPandas(
            score_pandas_dataframe_spark, schema=output_schema  # type: ignore
        )
        # ^ mypy says incompatible type and I don't know how to fix it

        return scores


def get_spark_master() -> str:
    active_session = _pyspark.sql.SparkSession.getActiveSession()
    if active_session:
        return active_session.conf.get("spark.master")

    if hasattr(_pyspark.SparkContext, "_active_spark_context"):
        active_context = _pyspark.SparkContext._active_spark_context
        if hasattr(active_context, "master") and active_context.master:
            return active_context.master

    return "local[*]"


def get_spark_session(
    app_name: str = "mlops_spark_scorer_job",
    mini_batch_size: int = 1000,
    master: _Optional[str] = None,
    spark_config: _Optional[_Dict[str, _Any]] = None,
) -> _pyspark_sql.SparkSession:
    if not spark_config:
        spark_config = {}
    conf = _pyspark.SparkConf()
    conf.setAppName(app_name)
    if master:
        conf.setMaster(master)
    if master and master.startswith("local"):
        driver_memory = conf.get("spark.driver.memory", "5g")
        conf.set("spark.driver.memory", driver_memory)
    conf.get("spark.sql.caseSensitive", "true")
    conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
    conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", str(mini_batch_size))
    conf.setAll([(k, str(v)) for k, v in spark_config.items()])
    spark = _pyspark_sql.SparkSession.builder.config(conf=conf).getOrCreate()
    return spark


def read_source(
    spark: _pyspark_sql.SparkSession,
    source_data: str,
    source_format: _configs.Format,
    source_config: _Optional[_Dict[str, str]] = None,
) -> _pyspark_sql.DataFrame:
    _source_config = _copy.copy(_configs.format_map[source_format])
    if source_config:
        _source_config.update(source_config)
    if source_format in [_configs.Format.JDBC_QUERY, _configs.Format.SNOWFLAKE_QUERY]:
        _source_config["query"] = source_data
    if source_format in [_configs.Format.JDBC_TABLE, _configs.Format.SNOWFLAKE_TABLE]:
        _source_config["dbtable"] = source_data
    if source_format in [
        _configs.Format.JDBC_QUERY,
        _configs.Format.JDBC_TABLE,
    ] and not _source_config.get("url"):
        raise RuntimeError("JDBC connection URL required for source.")
    if source_format in [
        _configs.Format.SNOWFLAKE_QUERY,
        _configs.Format.SNOWFLAKE_TABLE,
    ]:
        required_sf_options = {
            "sfDatabase",
            "sfURL",
            "sfUser",
        }
        missing_sf_options = required_sf_options.difference(_source_config.keys())
        if missing_sf_options:
            raise RuntimeError(
                f"Snowflake option(s) {missing_sf_options} required for source."
            )

    if source_format in [
        _configs.Format.JDBC_QUERY,
        _configs.Format.JDBC_TABLE,
        _configs.Format.SNOWFLAKE_QUERY,
        _configs.Format.SNOWFLAKE_TABLE,
    ]:
        return spark.read.load(**_source_config)
    else:
        return spark.read.load(source_data, **_source_config)


def write_sink(
    scored_sdf: _pyspark_sql.DataFrame,
    sink_location: str,
    sink_format: _configs.Format,
    sink_write_mode: _configs.WriteMode,
    sink_config: _Optional[_Dict[str, str]] = None,
) -> None:
    _sink_config = _copy.copy(_configs.format_map[sink_format])
    if sink_config:
        _sink_config.update(sink_config)
    if sink_format in [_configs.Format.JDBC_QUERY, _configs.Format.SNOWFLAKE_QUERY]:
        _sink_config["query"] = sink_location
    if sink_format in [_configs.Format.JDBC_TABLE, _configs.Format.SNOWFLAKE_TABLE]:
        _sink_config["dbtable"] = sink_location
    if sink_format in [
        _configs.Format.JDBC_QUERY,
        _configs.Format.JDBC_TABLE,
    ] and not _sink_config.get("url"):
        raise RuntimeError("JDBC connection URL required for sink.")
    if sink_format in [
        _configs.Format.SNOWFLAKE_QUERY,
        _configs.Format.SNOWFLAKE_TABLE,
    ]:
        required_sf_options = {
            "sfDatabase",
            "sfURL",
            "sfUser",
        }
        missing_sf_options = required_sf_options.difference(_sink_config.keys())
        if missing_sf_options:
            raise RuntimeError(
                f"Snowflake option(s) {missing_sf_options} required for sink."
            )

    mode = _copy.copy(_configs.write_mode_map[sink_write_mode])

    if sink_format in [
        _configs.Format.JDBC_QUERY,
        _configs.Format.JDBC_TABLE,
        _configs.Format.SNOWFLAKE_QUERY,
        _configs.Format.SNOWFLAKE_TABLE,
    ]:
        scored_sdf.write.mode(mode).save(**_sink_config)
    else:
        scored_sdf.write.mode(mode).save(sink_location, **_sink_config)
