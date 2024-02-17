from pathlib import Path

import httpx
import pytest
import yaml

from openapi_schema_validator import validate
from .fixtures import (
    conformance_page,
    conformance_classes,
    schema_dir,
    http_client,
    instance_url,
)


def test_ast7(conformance_page: httpx.Response):
    """/ats/core/conformance-op
    Test Purpose
        Validate that a Conformance Declaration can be retrieved from the expected location.

    Test Method
        - Construct a path for each "conformance" link on the landing page as well as for the {root}/conformance path.
        - Issue an HTTP GET request on each path
        - Validate that a document was returned with a status code 200
        - Validate the contents of the returned document using test /ats/core/conformance-success.
    """
    assert (
        conformance_page.status_code == 200
    ), f"{conformance_page.url.path} did not return a status code of 200"


def test_ast8(
    schema_dir: Path, conformance_page: httpx.Response, conformance_classes: list
):
    """/ats/core/conformance-success
    Test Purpose
        Validate that the Conformance Declaration response complies with the required structure and contents.

    Test Method
        - Validate the response document against OpenAPI 3.0 schema confClasses.yaml
        - Validate that the document includes the conformance class "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core"
        - Validate that the document list all OGC API conformance classes that the API implements.
    """
    with open(schema_dir / "confClasses.yaml") as file:
        schema = yaml.safe_load(file)
    response_json = conformance_page.json()
    requirement_class = "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core"
    validate(response_json, schema)
    assert (
        requirement_class in conformance_classes
    ), f"OGC Features API Core requirement class ({requirement_class}) is not listed in the conformsTo property."
