from pathlib import Path

import httpx
import yaml
from jsonschema.exceptions import ValidationError
from openapi_schema_validator import OAS30Validator, validate
from referencing import Registry

from .fixtures import (
    collections_page,
    collections_limit,
    http_client,
    instance_url,
    collections,
    registry,
    schema_dir,
)
from .utils import get_links_by_rel, check_links_rel_type


def test_ast9(collections_page: httpx.Response):
    """/ats/core/fc-md-op
    Test Purpose
        Validate that information about the Collections can be retrieved from the expected location.

    Test Method
        - Issue an HTTP GET request to the URL {root}/collections
        - Validate that a document was returned with a status code 200
        - Validate the contents of the returned document using test /ats/core/fc-md-success.
    """
    assert (
        collections_page.status_code == 200
    ), f"{collections_page.url.path} did not return 200"


def test_ast10(
    collections_page: httpx.Response,
    collections: list[dict],
    schema_dir: Path,
    registry: Registry,
):
    """/ats/core/fc-md-success
    Test Purpose
        Validate that the Collections content complies with the required structure and contents.

    Test Method
        - Validate that all response documents comply with /ats/core/fc-md-links
        - Validate that all response documents comply with /ats/core/fc-md-items
        - In case the response includes a "crs" property, validate that the first value is either "http://www.opengis.net/def/crs/OGC/1.3/CRS84" or "http://www.opengis.net/def/crs/OGC/0/CRS84h"
        - Validate the collections content for all supported media types using the resources and tests identified in Schema and Tests for Collections content
    """
    assert (
        get_links_by_rel(collections_page, "self") != []
    ), f"{collections_page.url.path} must contain a link with rel == self"
    assert check_links_rel_type(
        collections_page
    ), f"all links given by {collections_page.url.path} must specify the rel and type parameter"

    with open(schema_dir / "collections.yaml") as file:
        schema = yaml.safe_load(file)
    validate(collections_page.json(), schema, cls=OAS30Validator, registry=registry)

    crs_requirement_classes = [
        "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
        "http://www.opengis.net/def/crs/OGC/1.3/CRS84H",
    ]
    for collection in collections:
        if collection.get("crs", None) is not None:
            assert (
                collection.get("crs")[0] in crs_requirement_classes
            ), f"The first value of crs for collection {collection} must be one of {crs_requirement_classes}"