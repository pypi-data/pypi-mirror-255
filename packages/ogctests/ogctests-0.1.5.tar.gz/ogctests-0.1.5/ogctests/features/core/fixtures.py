import os
import re
import warnings
from pathlib import Path

import yaml
import httpx
import pytest
from dotenv import load_dotenv
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from .utils import (
    get_collection_responses,
    get_links_from_header,
    get_features_responses,
    get_feature_responses,
)


@pytest.fixture(scope="session")
def paging_limit():
    return 3


@pytest.fixture(scope="session")
def collections_limit():
    return 20


@pytest.fixture(scope="session")
def schema_dir():
    return Path(__file__).parent.parent / "schemas"


@pytest.fixture(scope="session")
def instance_url() -> str:
    load_dotenv()
    return os.environ.get("INSTANCE_URL")


@pytest.fixture(scope="session")
def http_client(instance_url: str) -> httpx.Client:
    with httpx.Client() as client:
        client.base_url = instance_url
        yield client


@pytest.fixture(scope="session")
def landing_page(http_client: httpx.Client) -> httpx.Response:
    return http_client.get("/")


@pytest.fixture(scope="session")
def api_links(landing_page: httpx.Response) -> list[dict]:
    try:
        api_links = [
            link
            for link in landing_page.json()["links"]
            if link["rel"] == "service-desc" or link["rel"] == "service-doc"
        ]
    except KeyError:
        try:
            links = get_links_from_header(landing_page.headers)
            api_links = [link for link in links if link["rel"] == ["service-doc"] or link["rel"] == ["service-desc"]]
        except KeyError:
            return []

    # HACK: because the demo.ldproxy.net test instances have a bug
    for i, link in enumerate(api_links):
        link["href"] = re.sub(r"(?<!:)//", "/", link["href"])
        api_links[i] = link

    return api_links


@pytest.fixture(scope="session")
def api_model(http_client: httpx.Client, api_links: list) -> dict:
    api_model = {}
    for link in api_links:
        # open api definition in json
        if link["type"] == "application/vnd.oai.openapi+json;version=3.0":
            response = httpx.get(link["href"])
            api_model = response.json()
        # open api definition in yaml
        elif link["type"] == "application/vnd.oai.openapi;version=3.0":
            response = httpx.get(link["href"])
            api_model = yaml.safe_load(response.content)
    return api_model


@pytest.fixture(scope="session")
def conformance_page(http_client: httpx.Client) -> httpx.Response:
    return http_client.get("/conformance")


@pytest.fixture(scope="session")
def conformance_classes(http_client: httpx.Client) -> list:
    response = http_client.get("/conformance")
    return response.json().get("conformsTo", [])


@pytest.fixture(scope="session")
def collections_page(http_client: httpx.Client) -> httpx.Response:
    return http_client.get("/collections", headers={"Accept": "application/json"})


@pytest.fixture(scope="session")
def collections(collections_page: httpx.Response, collections_limit: int) -> list[dict]:
    collections = collections_page.json().get("collections", [])
    if len(collections) > collections_limit:
        collections = collections[:collections_limit]
    return collections


@pytest.fixture(scope="session")
def collection_responses(
    collections: list[dict], http_client: httpx.Client
) -> list[dict]:
    return get_collection_responses(collections, http_client)


@pytest.fixture(scope="session")
def features_responses(
    collections: list[dict], http_client: httpx.Client
) -> list[dict]:
    return get_features_responses(collections, http_client)


@pytest.fixture(scope="module")
def feature_responses(features_responses: list[dict], http_client) -> list[dict]:
    features_limit = 100
    return get_feature_responses(features_responses, http_client, features_limit)


@pytest.fixture(scope="session")
def registry(schema_dir: Path):
    files = schema_dir.glob("*.yaml")
    resources = []
    for file in files:
        with open(file) as f:
            schema = yaml.safe_load(f)
        resource = Resource.from_contents(schema, default_specification=DRAFT202012)
        resources.append((f"urn:{file.name.replace('.yaml', '')}", resource))
    registry = Registry().with_resources(resources)
    return registry
