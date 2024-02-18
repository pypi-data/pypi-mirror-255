import warnings

import pytest
import httpx
import yaml

from datetime import datetime, timezone


@pytest.fixture(scope="session")
def features_limit():
    return 100


def get_links_from_header(headers: dict) -> dict:
    links = {}
    link_strings = headers["link"]
    for link_string in link_strings:
        fragments = link_string.split(",")
        for i, fragment in enumerate(fragments):
            links[i] = {}
            fragment.strip()
            if fragment.startswith("<") and fragment.endswith(">"):
                links[i]["href"] = fragment[1:-1]
            else:
                k, v = fragment.split("=").strip('"')
                links[i][k] = v
    return links


def get_links_by_rel(
    response: httpx.Response, rel: str, only_first: bool = False
) -> list | dict:
    """get all the links where link["rel"] == rel

    optionally only return the first link to meet the criteria
    """
    links = response.json().get("links", [])
    filtered = [link for link in links if link.get("rel") == rel]
    if only_first and len(filtered) > 0:
        return filtered[0]
    return filtered


def check_links_rel_type(response: httpx.Response) -> bool:
    """Check if all links specify the rel and type parameters"""
    links = response.json().get("links", [])
    if not links:
        return False
    for link in links:
        if link.get("rel", None) is None or link.get("type", None) is None:
            return False
    return True


def resolve_json_schema_ref(model: dict, reference: str) -> dict:
    """assumes ref of type: [http.*.(yaml|json)]#/.../..."""
    url = reference[0 : reference.find("#")] if reference.startswith("http") else ""
    if url:
        response = httpx.get(url)
        if response.headers.get("Content-Type") == "application/json":
            model = response.json()
        elif "yaml" in response.headers.get("Content-Type") or response.headers.get(
            "Content-Type"
        ).startswith("text/plain"):
            try:
                model = yaml.safe_load(response.content)
            except yaml.YAMLError:
                warnings.warn(f"could not decode json schema $ref at {url}")
                return {}
    reference_fragments = reference[reference.find("#") :].split("/")
    obj = model
    for fragment in reference_fragments[1:]:
        try:
            obj = obj[fragment]
        except KeyError:
            warnings.warn(
                f"Could not resolve the json schema $ref {reference} in the api model."
            )
            return {}
    return obj


def get_api_parameter(model: dict, path: str, parameter_name: str) -> dict:
    try:
        path_params = model["paths"][path]["parameters"]
    except KeyError:
        path_params = []
    for param in path_params:
        if "$ref" in param.keys():
            param = resolve_json_schema_ref(model, param["$ref"])
        if param.get("name") == parameter_name:
            return param
    try:
        get_params = model["paths"][path]["get"]["parameters"]
    except KeyError:
        get_params = []
    for param in get_params:
        if "$ref" in param.keys():
            param = resolve_json_schema_ref(model, param["$ref"])
        if param.get("name") == parameter_name:
            return param
    return {}


def get_collection_responses(
    collections: list[dict], http_client: httpx.Client
) -> list[dict]:
    responses = []
    for collection in collections:
        collectionId = collection["id"]
        path = f"/collections/{collectionId}"
        response = dict()
        response["id"] = collectionId
        response["response"] = http_client.get(path)
        responses.append(response)
    return responses


def get_features_responses(
    collections: list[dict],
    http_client: httpx.Client,
    headers: dict = {"Accept": "application/geo+json"},
    params: dict = None,
) -> list[dict]:
    responses = []
    for collection in collections:
        collectionId = collection["id"]
        path = f"/collections/{collectionId}/items"
        response = dict()
        response["id"] = collectionId
        response["before"] = datetime.now(tz=timezone.utc)
        response["response"] = http_client.get(path, headers=headers, params=params)
        response["after"] = datetime.now(tz=timezone.utc)
        responses.append(response)
    return responses


def get_feature_responses(
    features_responses: list[dict], http_client: httpx.Client, features_limit: int
) -> list[dict]:
    feature_responses = []
    for response in features_responses:
        features = response["response"].json().get("features", [])
        if not features:
            warnings.warn(f"No features found in collection: {response['id']}")
            break
        for i, feature in enumerate(features):
            if i > features_limit:
                break
            path = f"/collections/{response['id']}/items/{feature['id']}"
            feature_response = dict(
                {"feature_id": feature["id"], "collection_id": response["id"]}
            )
            feature_response["response"] = http_client.get(
                path, headers={"Accept": "application/geo+json"}
            )
            feature_responses.append(feature_response)
    return feature_responses
