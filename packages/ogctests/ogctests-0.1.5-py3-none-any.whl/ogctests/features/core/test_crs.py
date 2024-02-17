import json

import geopandas as gpd

from .fixtures import conformance_classes, http_client, instance_url


def test_ast2(conformance_classes: list):
    """/ats/core/crs84
    Test Purpose
        Validate that all spatial geometries provided through the API are in the CRS84 spatial reference system unless
        otherwise requested by the client.

    Test Method
        - Do not specify a coordinate reference system in any request.
            All spatial data should be in the CRS84 reference system.
        - Validate retrieved spatial data using the CRS84 reference system.
    """
    crs_conformance_class = "http://www.opengis.net/spec/ogcapi-features-2/1.0/conf/crs"
    assert (
        crs_conformance_class in conformance_classes
    ), f"OGC Features API CRS conformance class {crs_conformance_class} is not listed in the conformsTo property."


def assert_valid_feature_crs(feature: dict):
    parsed_feature = gpd.read_file(json.dumps(feature), driver="GeoJSON")
    assert (parsed_feature.crs.name.startswith("WGS 84")), \
        f"feature not in CRS format. expected WGS84 or WGS84H got {parsed_feature.crs.name}"
