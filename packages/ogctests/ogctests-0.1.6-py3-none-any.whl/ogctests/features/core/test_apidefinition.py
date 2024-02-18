from pathlib import Path

import httpx
import yaml
from jsonschema.exceptions import ValidationError

from openapi_schema_validator import validate, OAS30Validator

from .fixtures import http_client, instance_url, api_links, api_model, landing_page, schema_dir


def test_ast5(http_client: httpx.Client, api_links: list[dict]):
    """/ats/core/api-definition-op
    Test Purpose
        Validate that the API Definition document can be retrieved from the expected location.
    Test Method
        - Construct a path for each API Definition link on the landing page
        - Issue a HTTP GET request on each path
        - Validate that a document was returned with a status code 200
        - Validate the contents of the returned document using test /ats/core/api-definition-success.
    """
    assert api_links != [], "No API Definitions provided by the server"
    for api_link in api_links:
        response = http_client.get(api_link["href"])
        assert (
            response.status_code == 200
        ), f"Listed API Definition unavailable ({api_link['href']})"


def test_ast6(schema_dir: Path, api_model: dict):
    """/ats/core/api-definition-success
    Test Purpose
        Validate that the API Definition complies with the required structure and contents.
    Test Method
        Validate the API Definition document against an appropriate schema document.
    """
    with open(schema_dir / "openapi_schema_v3.0.yaml", "r") as file:
        schema = yaml.safe_load(file)
    validate(api_model, schema, cls=OAS30Validator)
