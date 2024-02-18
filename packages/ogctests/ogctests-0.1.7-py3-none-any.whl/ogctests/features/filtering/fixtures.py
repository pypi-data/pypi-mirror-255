import os
import re
import warnings
from pathlib import Path

import yaml
import httpx
import pytest
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    pass
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


@pytest.fixture(scope="session")
def instance_url() -> str:
    try:
        load_dotenv()
    except NameError:
        pass
    return os.environ.get("INSTANCE_URL")


@pytest.fixture(scope="session")
def http_client(instance_url: str) -> httpx.Client:
    with httpx.Client() as client:
        client.base_url = instance_url
        yield client
