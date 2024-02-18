import httpx
from .fixtures import http_client, instance_url, collections, collections_page, collections_limit


def test_ast20(collections: list[dict], http_client: httpx.Client):
    """/ats/core/query-param-invalid
    Test Purpose
        Validate that the API correctly deals with invalid query parameters.

    Test Method
        - Enter an HTTP request with an invalid query parameter.
        - Verify that the API returns the status code 400.
    """
    for collection in collections:
        path = f"/collections/{collection['id']}/items"
        param = {"limit": "unlimited"}
        response = http_client.get(path, params=param)
        assert (
            response.status_code == 400
        ), f"{path} did not respond 400 to an invalid query parameter: {param}"


def test_ast21(collections: list[dict], http_client: httpx.Client):
    """/ats/core/query-param-unknown
    Test Purpose
        Validate that the API correctly deals with unknown query parameters.

    Test Method
        - Enter an HTTP request with an query parameter that is not specified in the API definition.
        - Verify that the API returns the status code 400.
    """
    for collection in collections:
        path = f"/collections/{collection['id']}/items"
        param = {"ooga": "booga"}
        response = http_client.get(path, params=param)
        assert (
            response.status_code == 400
        ), f"{path} did not respond 400 to an unknown query parameter: {param}"
