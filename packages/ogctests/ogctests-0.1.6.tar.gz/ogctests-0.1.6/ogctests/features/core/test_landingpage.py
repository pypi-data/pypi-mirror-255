import warnings
from pathlib import Path

import httpx
import pytest
import yaml
from jsonschema.exceptions import ValidationError

from referencing import Resource, Registry
from openapi_schema_validator import validate

from .fixtures import http_client, instance_url, landing_page, schema_dir, registry
from .utils import get_links_by_rel


def test_ast3(http_client: httpx.Client):
    """/ats/core/root-op
    Test Purpose
        Validate that a landing page can be retrieved from the expected location.

    Test Method
        - Issue an HTTP GET request to the URL {root}/
        - Validate that a document was returned with a status code 200
        - Validate the contents of the returned document using test /ats/core/root-success.
    """
    response = http_client.get("/", headers={"Accept": "application/json"})
    assert response.status_code != 405, "Get operation not supported at /"
    assert (
        response.status_code == 200
    ), "Response was not returned with status code 200"


def test_ast4(landing_page: httpx.Response, schema_dir: Path, registry: Registry, http_client):
    """/ats/core/root-success
    Test Purpose
        Validate that the landing page complies with the require structure and contents.

    Test Method
        - Validate the landing page for all supported media types using the resources and tests identified in
          Schema and Tests for Landing Pages
        - For formats that require manual inspection, perform the following:
        - Validate that the landing page includes a "service-desc" and/or "service-doc" link to an API Definition
        - Validate that the landing page includes a "conformance" link to the conformance class declaration
        - Validate that the landing page includes a "data" link to the Feature contents.
    """
    if landing_page.headers.get("Content-Type") != "application/json":
        landing_page = http_client.get("/", headers={"Accept": "application/json"})
        if landing_page.status_code != 200 or landing_page.headers.get("Content-Type") != "application/json":
            pytest.skip("The landing page could not be retrieved in JSON. Manual inspection required.")

    with open(schema_dir / "landingPage.yaml") as file:
        schema = yaml.safe_load(file)

    validate(landing_page.json(), schema, registry=registry)

    service_desc = get_links_by_rel(landing_page, "service-desc")
    service_doc = get_links_by_rel(landing_page, "service-doc")
    conformance = get_links_by_rel(landing_page, "conformance")
    data = get_links_by_rel(landing_page, "data")

    assert any([service_desc, service_doc]) and all(
        [conformance, data]
    ), """The landing page must include at least links with relation type ('service-desc' or 'service-doc'),\
        and 'conformance' and 'data'\
        """