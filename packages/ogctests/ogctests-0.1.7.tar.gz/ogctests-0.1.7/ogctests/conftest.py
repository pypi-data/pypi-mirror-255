import os
import pytest


@pytest.fixture(scope="session")
def instance_url() -> str:
    try:
        load_dotenv()
    except NameError:
        pass
    return os.environ.get("INSTANCE_URL", "")


@pytest.fixture(scope="session", autouse=True)
def suite_props(record_testsuite_property, instance_url):
    record_testsuite_property("instance-url", instance_url)
