import httpx
from .fixtures import http_client, instance_url


def test_ct6(http_client: httpx.Client):
    """/conf/filter/get-conformance
    Test Purpose
        Check that the API declares support for the conformance class

    Test Method
        Given:

            n/a

        When:

            the request for the Conformance Declaration is executed

                method: GET

                path: {apiURI}/conformance

                header: Accept: application/json

                authentication, if authentication credentials are provided

        Then:

            assert successful execution (status code is "200", Content-Type header is "application/json");

            assert that $.conformsTo is a string array that includes the value "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/filter".
    """
    response = http_client.get("/conformance", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    conforms_to = response.json().get("conformsTo")
    assert isinstance(conforms_to, list)
    assert (
        "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/filter" in conforms_to
    )


def test_ct7(http_client: httpx.Client):
    """/conf/filter/filter-param
    Test Purpose
        Check that the query parameter filter is supported

    Test Method
        Given:

            test "get-queryables" was successful

            the list of filterable resources

            the sample queryable of every filterable resource

        When:

            a request for each resource that supports filtering is executed without a filter parameter

                method: GET

                path: {apiURI}/{pathToResource}

                header: Accept: {responseMediaType}

                authentication, if authentication credentials are provided

        Then:

            assert successful execution (the status code is in the list of acceptable status codes for a successful execution, Content-Type header is {responseMediaType});

            store the result as the unfiltered result of the resource.

        When:

            a request for each resource that supports filtering is executed with a valid filter expression

                method: GET

                path: {apiURI}/{pathToResource}

                query parameters (before percent encoding): filter-lang={filter-lang}&filter={filter-valid} where {queryable} in {filter-valid} is replaced by the sample queryable of the filterable resource

                header: Accept: {responseMediaType}

                authentication, if authentication credentials are provided

        Then:

            assert successful execution (the status code is in the list of acceptable status codes for a successful execution, Content-Type header is {responseMediaType});

            assert that each returned resource matches the filter expression.

        When:

            a request for each resource that supports filtering is executed with an invalid filter expression

                method: GET

                path: {apiURI}/{pathToResource}

                query parameters (before percent encoding): filter-lang={filter-lang}&filter={filter-invalid} where {queryable} in {filter-invalid} is replaced by the sample queryable of the filterable resource

                header: Accept: {responseMediaType}

                authentication, if authentication credentials are provided

        Then:

            assert unsuccessful execution (the status code is in the list of acceptable status codes for an unsuccessful execution).


    """
    pass
