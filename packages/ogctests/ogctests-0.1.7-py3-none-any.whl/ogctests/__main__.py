import sys
import os
from datetime import datetime
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
        package="ogctests",
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
    epilog=epilog,
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
parser.add_argument(
    "-r",
    "--report",
    type=bool,
    help="set True to enable report generation.",
    default=False,
    dest="report",
)
parser.add_argument(
    "-v",
    "--verbose",
    type=bool,
    help="set True to for verbose output",
    dest="verbose"
)
args = parser.parse_args()
os.environ["INSTANCE_URL"] = args.iurl
arglist = [str(root_dir / path) for path in args.scope]
if not args.verbose:
    arglist += ["--no-header", "--no-summary", "-p no:warnings", "--tb=no"]
if args.report:
    report_folder = os.path.expanduser("~") + "/ogctestsReporting"
    report_name = f"testrun-{datetime.now():%Y-%m-%d}.xml"
    if not os.path.exists(report_folder):
        os.mkdir(report_folder)
    arglist += [f"--junit-xml={report_folder}/{report_name}"]
print(f"\n\nTesting endpoint: {args.iurl}")
pytest.main(args=arglist)
if args.report:
    print(f"Report saved to {report_folder}/{report_name}\n\n")
