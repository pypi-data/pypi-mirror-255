import warnings
from pathlib import Path

import httpx
import pytest
import yaml
from jsonschema.exceptions import ValidationError
from openapi_schema_validator import validate
from referencing import Registry

from .fixtures import (
    feature_responses,
    features_responses,
    collections,
    collections_page,
    collections_limit,
    http_client,
    instance_url,
    schema_dir,
    registry,
)
from .utils import get_links_by_rel, check_links_rel_type


def test_ast27(feature_responses: list[dict]):
    """/ats/core/f-op
    Test Purpose
        Validate that a feature can be retrieved from the expected location.

    Test Method
        - For a sufficiently large subset of all features in a feature collection (path /collections/{collectionId}),
          issue an HTTP GET request to the URL /collections/{collectionId}/items/{featureId} where {collectionId}
          is the id property for the collection and {featureId} is the id property of the feature.
        - Validate that a feature was returned with a status code 200
        - Validate the contents of the returned feature using test /ats/core/f-success
    """
    for response in feature_responses:
        assert (
            response["response"].status_code == 200
        ), f"feature {response['feature_id']}, did not return 200 at {response['response'].url.path} (status code: {response['response'].status_code})"


def test_ast28(feature_responses: list[dict], schema_dir: Path, registry: Registry):
    """/ats/core/f-success
    Test Purpose
        Validate that the Feature complies with the required structure and contents.

    Test Method
        - Validate that the Feature includes all required link properties using /ats/core/f-links
        - Validate the Feature for all supported media types using the resources and tests
          identified in Schema and Tests for Features
    """
    with open(schema_dir / "featureGeoJSON.yaml") as file:
        schema = yaml.safe_load(file)
    for response in feature_responses:
        feature = response["response"].json()
        if not feature:
            warnings.warn(f"No feature returned for feature {response['feature_id']} in collection {response['collection_id']}")
            break
        validate(feature, schema, registry=registry)


def test_ast29(feature_responses):
    """/ats/core/f-links
    Test Purpose
        Validate that the required links are included in a Feature.

    Test Method
        Verify that the returned Feature includes:
            - a link to this response document (relation: self),
            - a link to the response document in every other media type supported by the server (relation: alternate).
            - a link to the feature collection that contains this feature (relation: collection).
        Verify that all links include the rel and type link parameters.
    """
    for response in feature_responses:
        assert (
            get_links_by_rel(response["response"], "self")
            and get_links_by_rel(response["response"], "collection")
            and check_links_rel_type(response["response"])
        ), f"Response for feature {response['feature_id']} in collection {response['collection_id']} must contain a link to itself and the parent collection and all links must specify the rel and type parameters."
