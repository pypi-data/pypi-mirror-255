from .fixtures import (
    collections,
    collection_responses,
    collections_limit,
    collections_page,
    http_client,
    instance_url,
)


def test_ast11(collection_responses: list[dict]):
    """/ats/core/sfc-md-op
    Test Purpose
        Validate that the Collection content can be retrieved from the
        expected location.

    Test Method
        For every Feature Collection described in the Collections content,
        - issue an HTTP GET request to the URL /collections/{collectionId} where
        {collectionId} is the id property for the collection.
        - Validate that a Collection was returned with a status code 200
        - Validate the contents of the returned document using test /ats/core/sfc-md-success.
    """
    for response in collection_responses:
        status_code = response["response"].status_code
        assert (
            status_code == 200
        ), f"/collections/{response['id']} responded with {status_code}, expected 200"


def test_ast12(collections: list[dict], collection_responses: list[dict]):
    """/ats/core/sfc-md-success
    Test Purpose
        Validate that the Collection content complies with the required structure and contents.

    Test Method
        Verify that the content of the response is consistent with the content for this
        Feature Collection in the /collections response. That is, the values for
        id, title, description and extent are identical.
    """
    for collection in collections:
        collectionId = collection["id"]
        response = [
            response["response"].json()
            for response in collection_responses
            if response["id"] == collectionId
        ][0]
        assert all(
            (
                collection.get("id") == response.get("id"),
                collection.get("title") == response.get("title"),
                collection.get("description") == response.get("description"),
                collection.get("extent") == response.get("extent"),
            ),
        ), f"The properties of the collection '{collectionId}' do not match what is stated at /collections"
