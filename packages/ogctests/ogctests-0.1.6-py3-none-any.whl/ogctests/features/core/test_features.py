import warnings
from pathlib import Path
from datetime import datetime, timezone
import json
import httpx
import pytest
import yaml

import geopandas as gpd
from shapely.geometry import Polygon

from openapi_schema_validator import validate
from referencing import Registry

from .fixtures import (
    collections,
    collections_page,
    collections_limit,
    http_client,
    instance_url,
    schema_dir,
    registry,
    api_model,
    api_links,
    landing_page,
    features_responses,
)
from .utils import (
    get_links_by_rel,
    check_links_rel_type,
    get_api_parameter,
    get_features_responses,
)

from .test_crs import assert_valid_feature_crs


@pytest.fixture(scope="module")
def bbox_responses() -> list:
    return []


def assert_bbox_in_range(feature: dict, bbox: str):
    ll_lon, ll_lat, ur_lon, ur_lat = bbox.split(",")
    corners = [(ll_lon, ll_lat), (ur_lon, ll_lat), (ur_lon, ur_lat), (ll_lon, ur_lat)]
    polygon = Polygon(corners)
    feature_gdf = gpd.read_file(json.dumps(feature), driver="GeoJSON")
    assert feature_gdf.intersects(polygon)[
        0
    ], f"""
        Returned features must intersect with the bounding box specified in the bbox parameter.
        bbox: {polygon}. 
        feature: (id: {feature['id']}). (geometries: {feature_gdf.geometry})
        """.strip()


def test_ast13(features_responses: list[dict]):
    """/ats/core/fc-op
    Test Purpose
        Validate that features can be identified and extracted from a Collection using query parameters.

    Test Method
        For every feature collection identified in Collections, issue an HTTP GET request to the URL /collections/{collectionId}/items
        where {collectionId} is the id property for a Collection described in the Collections content.
        - Validate that a document was returned with a status code 200.
        - Validate the contents of the returned document using test /ats/core/fc-response.
        - Repeat these tests using the following parameter tests:
            - Bounding Box:
                Parameter /ats/core/fc-bbox-definition
                Response /ats/core/fc-bbox-response
            - Limit:
                Parameter /ats/core/fc-limit-definition
                Response /ats/core/fc-limit-response
            - DateTime:
                Parameter /ats/core/fc-time-definition
                Response /ats/core/fc-time-response
        Error conditions:
            Query Invalid /ats/core/query-param-invalid
            Query Unknown /ats/core/query-param-unknown
        Execute requests with combinations of the "bbox" and "datetime" query parameters and verify that only
        features are returned that match both selection criteria.
    """
    for response in features_responses:
        status_code = response["response"].status_code
        assert (
            status_code == 200
        ), f"/collections/{response['id']}/items responded with {status_code}, expected 200"


def test_ast14(
    collections: list[dict],
    api_model: dict,
):
    """/ats/core/fc-bbox-definition
    Test Purpose
        Validate that the bounding box query parameters are constructed correctly.

    Test Method
        - Verify that the bbox query parameter complies with the following definition
          (using an OpenAPI Specification 3.0 fragment):

                name: bbox
                in: query
                required: false
                schema:
                  type: array
                  minItems: 4
                  maxItems: 6
                  items:
                    type: number
                style: form
                explode: false

        - Use a bounding box with four numbers in all requests:
            Lower left corner, WGS 84 longitude
            Lower left corner, WGS 84 latitude
            Upper right corner, WGS 84 longitude
            Upper right corner, WGS 84 latitude
    """
    for collection in collections:
        path = f"/collections/{collection['id']}/items"
        bbox_def = get_api_parameter(api_model, path, "bbox")
        if not bbox_def:
            warnings.warn(f"bbox parameter missing from {path}")
        else:
            assert (
                bbox_def.get("in") == "query"
                and not bbox_def.get("required")
                and bbox_def.get("schema").get("type") == "array"
                and bbox_def.get("schema").get("minItems") == 4
                and bbox_def.get("schema").get("maxItems") == 6
                and bbox_def.get("schema").get("items").get("type") == "number"
                and bbox_def.get("style") == "form"
                and not bbox_def.get("explode")
            ), f"bbox parameter ill defined at {path}"


def test_ast15(
    collections: list[dict],
    http_client: httpx.Client,
    bbox_responses: list,
    bbox: str = "5,48,20,70",
):
    """/ats/core/fc-bbox-response
    Test purpose
        Validate that the bounding box query parameters are processed corrrectly.

    Test Method
        - Verify that only features that have a spatial geometry that intersects the bounding box
          are returned as part of the result set.
        - Verify that the bbox parameter matched all features in the collection that were not
          associated with a spatial geometry (this is only applicable for datasets that include
          features without a spatial geometry).
        - Verify that the coordinate reference system of the geometries is WGS 84 longitude/latitude
          ("http://www.opengis.net/def/crs/OGC/1.3/CRS84" or "http://www.opengis.net/def/crs/OGC/0/CRS84h")
          since no parameter bbox-crs was specified in the request.
    """
    if not bbox_responses:
        bbox_responses = get_features_responses(
            collections, http_client, params={"bbox": bbox}
        )
    for response in bbox_responses:
        data = response["response"].json()
        for i, feature in enumerate(data.get("features", [])):
            # as per official test suite. stop after checking 100 features
            if i > 100:
                break
            assert_bbox_in_range(feature, bbox)
            assert_valid_feature_crs(feature)


def test_ast16(collections: list[dict], api_model: dict):
    """/ats/core/fc-limit-definition
    Test Purpose
        Validate that the limit query parameters are constructed corrrectly.

    Test Method
        - Verify that the limit query parameter complies with the following definition
          (using an OpenAPI Specification 3.0 fragment):

                name: limit
                in: query
                required: false
                schema:
                  type: integer
                style: form
                explode: false
        - Note that the API can define values for "minimum", "maximum" and "default".
    """
    for collection in collections:
        path = f"/collections/{collection['id']}/items"
        limit_def = get_api_parameter(api_model, path, "limit")
        if not limit_def:
            warnings.warn(f"limit parameter missing from {path}")
        else:
            assert (
                limit_def.get("in") == "query"
                and not limit_def.get("required")
                and limit_def.get("schema").get("type") == "integer"
                and limit_def.get("style") == "form"
                and not limit_def.get("explode")
            ), f"limit parameter ill defined at {path}"


def test_ast17(collections: list[dict], http_client: httpx.Client, limit: int = 5):
    """/ats/core/fc-limit-response
    Test Purpose
        Validate that the limit query parameters are processed correctly.

    Test Method
        - Count the Features which are on the first level of the collection. Any nested objects contained
          within the explicitly requested items are not be counted.
        - Verify that this count is not greater than the value specified by the limit parameter.
        - If the API definition specifies a maximum value for limit parameter, verify that the count does
          not exceed this maximum value.
    """
    features_responses = get_features_responses(collections, http_client, params={"limit": limit})
    for response in features_responses:
        features = response["response"].json().get("features", [])
        if not features:
            warnings.warn(f"No features returned from {response['response'].url.path}")
            break
        assert (
            len(features) <= limit
        ), f"Number of features exceeds the limit parameter value, limit: {limit}, received {len(features)}"


def test_ast18(collections: list[dict], api_model: dict):
    """/ats/core/fc-time-definition
    Test Purpose
        Validate that the dateTime query parameters are constructed correctly.

    Test Method
        - Verify that the datetime query parameter complies with the following definition
          (using an OpenAPI Specification 3.0 fragment):

            name: datetime
            in: query
            required: false
            schema:
                type: string
            style: form
            explode: false
    """
    for collection in collections:
        path = f"/collections/{collection['id']}/items"
        datetime_def = get_api_parameter(api_model, path, "datetime")
        if not datetime_def:
            warnings.warn(f"datetime parameter missing from {path}")
        else:
            assert (
                datetime_def.get("in") == "query"
                and not datetime_def.get("required")
                and datetime_def.get("schema").get("type") == "string"
                and datetime_def.get("style") == "form"
                and not datetime_def.get("explode")
            ), f"datetime parameter ill defined at {path}"


def test_ast19(collections: list[dict], http_client: httpx.Client):
    """/ats/core/fc-time-response
    Test Purpose
        Validate that the dataTime query parameters are processed correctly.

    Test Method
        - Verify that only features that have a temporal geometry that intersects the temporal information
          in the datetime parameter were included in the result set
        - Verify that all features in the collection that are not associated with a temporal geometry are
          included in the result set
        - Validate that the datetime parameter complies with the syntax described in /req/core/fc-time-response.
    """
    date_time = "2015-01-01/2024-01-01"
    responses = get_features_responses(
        collections, http_client, params={"dateTime": date_time}
    )
    for response in responses:
        # This test not implemented in the official test suite either
        assert response


def test_ast22(
    schema_dir: Path,
    registry: Registry,
    features_responses: list[dict],
):
    """/ats/core/fc-response
    Test Purpose
        Validate that the Feature Collections complies with the require structure and contents.

    Test Method
        - Validate that the type property is present and has a value of FeatureCollection
        - Validate the features property is present and that it is populated with an array of feature items.
        - Validate that only Features which match the selection criteria are included in the Feature Collection.
        - If the links property is present, validate that all entries comply with /ats/core/fc-links
        - If the timeStamp property is present, validate that it complies with /ats/core/fc-timeStamp
        - If the numberMatched property is present, validate that it complies with /ats/core/fc-numberMatched
        - If the numberReturned property is present, validate that it complies with /ats/core/fc-numberReturned
        - Validate the collections content for all supported media types using the resources and tests identified in
          Schema and Tests for Feature Collections
    """
    with open(schema_dir / "featureCollectionGeoJSON.yaml") as file:
        schema = yaml.safe_load(file)
    for response in features_responses:
        assert (
            response["response"].json().get("features", [])
        ), f"No features listed at /collections/{response['id']}/items"
        validate(response["response"].json(), schema, registry=registry)


def test_ast23(features_responses: list[dict]):
    """/ats/core/fc-links
    Test Purpose
        Validate that the required links are included in the Collections document.

    Test Method
        Verify that the response document includes:
            - a link to this response document (relation: self),
            - a link to the response document in every other media type supported by the server (relation: alternate).
            - Verify that all links include the rel and type link parameters.
    """
    for response in features_responses:
        assert get_links_by_rel(
            response["response"], "self"
        ), f"The response from /collections/{response['id']}/items does not contain a link to itself."
        assert check_links_rel_type(
            response["response"]
        ), f"Not all links contain a rel and type parameter at /collections/{response['id']}/items"


def test_ast24(
    features_responses: list[dict],
):
    """/ats/core/fc-timeStamp
    Test Purpose
        Validate the timeStamp parameter returned with a Features response

    Test Method
        Validate that the timeStamp value is set to the time when the response was generated.
    """
    for response in features_responses:
        ts_before = response["before"]
        ts_after = response["after"]
        try:
            ts = datetime.fromisoformat(
                response["response"].json().get("timeStamp", "")
            )
        except ValueError:
            warnings.warn(f"No timestamp given at {response['id']}")
            break
        assert (
            ts_before <= ts <= ts_after
        ), f"unexpected value for timeStamp. Expected: {ts_before:%Y-%m-%dT%H:%M:%S} <= {ts:%Y-%m-%dT%H:%M:%S} <= {ts_after:%Y-%m-%dT%H:%M:%S}"

def test_ast25(
    collections: list[dict], http_client: httpx.Client, bbox_responses: list, bbox: str = "5,48,20,70"
):
    """/ats/core/fc-numberMatched
    Test Purpose
        Validate the numberMatched parameter returned with a Features response

    Test Method
        Validate that the value of the numberMatched parameter is identical to the number of features
        in the feature collections that match the selection parameters like bbox, datetime or
        additional filter parameters.
    """
    if not bbox_responses:
        bbox_responses = get_features_responses(
            collections, http_client, params={"bbox": bbox}
        )
    for response in bbox_responses:
        data = response["response"].json()
        numberMatched = data.get("numberMatched", -1)
        if numberMatched == -1:
            warnings.warn(f"numberMatched parameter not given at {response['id']}")
            break
        features = data.get("features", [])
        nxt_link = get_links_by_rel(response["response"], "next", only_first=True)
        total_returned = len(features)
        while nxt_link:
            nxt_page = http_client.get(url=nxt_link["href"], headers={"Accept": "application/geo+json"})
            features = nxt_page.json().get("features", [])
            nxt_link = get_links_by_rel(nxt_page, "next", only_first=True)
            total_returned += len(features)
        assert (
            total_returned == numberMatched
        ), f"numberMatched parameter claims {numberMatched} features. but {total_returned} were found."


def test_ast26(
    collections: list[dict], http_client: httpx.Client, bbox_responses: list, bbox: str = "5,48,20,70"
):
    """/ats/core/fc-numberReturned
    Test Purpose
        Validate the numberReturned parameter returned with a Features response

    Test Method
        Validate that the numberReturned value is identical to the number of features in the response
    """

    if not bbox_responses:
        bbox_responses = get_features_responses(
            collections, http_client, params={"bbox": bbox}
        )
    for response in bbox_responses:
        data = response["response"].json()
        numberReturned = data.get("numberReturned", -1)
        if numberReturned == -1:
            warnings.warn(f"numberReturned parameter not given at {response['id']}")
            break
        total_returned = len(data.get("features", []))
        assert (
            total_returned == numberReturned
        ), f"numberReturned parameter claims {numberReturned} features. but got {total_returned}"
