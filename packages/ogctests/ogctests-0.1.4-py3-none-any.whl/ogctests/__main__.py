import sys
import os
import argparse
import inspect
from importlib import import_module
from pathlib import Path

import pytest


root_dir = Path(__file__).parent
test_files = root_dir.glob("features/core/test_*.py")
epilog = """
features/
  core/
"""
for file in test_files:
    epilog += "    " + str(file.name) + "::\n"
    module = import_module(
        "." + str(file)[str(file).find("features"):].replace("/", ".").replace(".py", ""),
        package="ogctests"
    )
    funcs = [
        func[0]
        for func in inspect.getmembers(module, inspect.isfunction)
        if func[0].startswith("test")
    ]
    for func in funcs:
        epilog += "      " + func + "\n"

parser = argparse.ArgumentParser(
    prog="ogctests",
    description="OGC API Test Suite",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=epilog
)
parser.add_argument(
    "scope", type=str, help="Specify tests to run", nargs="+", default="features/core"
)
parser.add_argument(
    "-i",
    "--instance-url",
    type=str,
    help="URL of the server to run the test suite against.",
    required=True,
    dest="iurl",
)
args = parser.parse_args()
os.environ["INSTANCE_URL"] = args.iurl

paths = [str(root_dir / path) for path in args.scope]
arglist = paths + ["--no-header", "--no-summary", "-p no:warnings", "--tb=no"]
pytest.main(args=arglist)
