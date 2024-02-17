import httpx

from .fixtures import http_client, instance_url


def test_ast1(http_client: httpx.Client):
    """/ats/core/http
    Test Purpose
        Validate that the resource paths advertised through the API conform with HTTP 1.1 and, where approprate, TLS.

    Test Method
        - All compliance tests shall be configured to use the HTTP 1.1 protocol exclusively.
        - For APIs which support HTTPS, all compliance tests shall be configured to use HTTP over
          TLS (RFC 2818) with their HTTP 1.1 protocol.
    """

    def check_http_version(response: httpx.Response):
        assert response.http_version == "HTTP/1.1"

    http_client.event_hooks["response"] = [check_http_version]
