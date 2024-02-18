import httpx
from .fixtures import http_client, instance_url


def test_ct1(http_client: httpx.Client):
    """/conf/queryables/get-conformance
    Test Purpose
        Check that the API declares support for the conformance class
    Test Method
        Given:

            n/a

        When:

            the request for the Conformance Declaration is executed

                method: GET

                path: {apiURI}/conformance

                authentication, if authentication credentials are provided

        Then:

            assert successful execution (status code is "200", Content-Type header is "application/json");

            assert that $.conformsTo is a string array that includes the value "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/queryables".
    """
    response = http_client.get("/conformance", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/json"
    conforms_to = response.json().get("conformsTo")
    assert isinstance(conforms_to, list)
    assert (
        "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/queryables"
        in conforms_to
    )


def ct2(http_client: httpx.Client):
    """/conf/queryables/get-queryables-uris
    Test Purpose
        Check that a link to the Queryables resource exists for every filterable resource
    Test Method
        Given:

            the list of filterable resources ({apiURI}/{pathToResource});

        When:

            a request is executed for every filterable resource

                method: HEAD (if HEAD results in a 405 response, use GET instead)

                path: {apiURI}/{pathToResource}

                header: Accept: application/json

                authentication, if authentication credentials are provided

        Then:

            assert successful execution (status code is "200");

            assert that the response includes a Link header with rel set to http://www.opengis.net/def/rel/ogc/1.0/queryables or [ogc-rel:queryables];

            store the href value as the Queryables URI for the filterable resource ({queryablesUri}).
    """
    pass
