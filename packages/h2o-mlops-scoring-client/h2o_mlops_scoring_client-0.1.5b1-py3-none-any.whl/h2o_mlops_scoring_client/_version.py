import importlib.resources


version = "0.0.0"

try:
    resource = importlib.resources.files(  # type: ignore
        "h2o_mlops_scoring_client"
    ).joinpath("VERSION")
    if resource.is_file():
        version = resource.read_text().strip()
except AttributeError:
    # fallback for Python < 3.9
    if importlib.resources.is_resource("h2o_mlops_scoring_client", "VERSION"):
        version = importlib.resources.read_text(
            "h2o_mlops_scoring_client", "VERSION"
        ).strip()
