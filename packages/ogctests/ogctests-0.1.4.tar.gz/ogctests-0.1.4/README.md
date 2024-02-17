# OGC API Test Client

A black box verifier for OGC API specifications

## What it Does

In line with the
[Official OGC test suite](https://github.com/opengeospatial/ets-ogcapi-features10)
(written in Java), this Python-based test suite will verify the compliance of a
given endpoint with the
[OGC API - Features - Part 1: Core](https://docs.ogc.org/is/17-069r3/17-069r3.html)
specification.

The test suite only tests against the **OGC API - Features - Part 1:
Core** specification, But may be expanded in the future.

## How to run the tests

The tests are run using [pytest](https://docs.pytest.org).

They are all contained in the `features/core/` directory and can be run with
pytest in the usual way.

The [Run Tests](https://github.com/Kurrawong/ogctests/actions/workflows/run_tests.yml) GitHub action is also available
to easily point the test suite
at a designated URL.

For example, to check if an endpoint complies with all the requirements of the
**OGC API - Features - Part 1: Core** specification, you could run:

```bash
$ pytest features/core
```

> **Note**: package dependencies are managed with
> [poetry](https://python-poetry.org/), so you will first need to run
> `poetry install` and `poetry shell` to install the dependencies and activate
> the virtual environment.

All the tests are written as class methods. Thus, a subset of the tests can be
run by scoping them with the usual pytest syntax.

For example, if you only want to test if the landing page is implemented
according to the specification, you could run:

```bash
$ pytest features/core/test_landingpage.py
```

> This would run the two tests in the TestLandingPage class;
>
> - test_ast3 (/req/core/root-op)
> - test_ast4 (/req/core/root-op-success)

To run the tests on a subset of classes in tests.py you can specify them as
follows:

```bash
$ pytest features/core/test_landingpage.py features/core/test_apidefinition.py
```

> This will run a total of four tests. Two from the TestLandingPage class and
> two from the TestDefinition class

## Reporting

In addition to the usual pytest output, a json report of test results is saved
to `results/testResults.json`. This report captures ...

> **Note**: Reporting not yet implemented.

## Testing the Tests

Somewhat confusingly, pytest is also used to test the tests. During development,
you may wish to check if all the OGC requirement tests defined in
`features/core/tests.py` are behaving as expected. To do this you would run
pytest in the usual way. For example:

```bash
$ pytest tests
```

> Note: This will run all the tests defined in the tests folder.

## OGC API Specification

OGC API — Features — Part 1: Core\
https://docs.ogc.org/is/17-069r3/17-069r3.html

Official OGC test suite  
https://github.com/opengeospatial/ets-ogcapi-features10

### Implementors

- https://demo.pygeoapi.io/stable
- https://demo.ldproxy.net/vineyards
- https://demo.ldproxy.net/daraa
- https://demo.ldproxy.net/zoomstack
- https://www.ldproxy.nrw.de/kataster

### Prez endpoint for testing

- http://localhost:8000/s/datasets/{dataset_curie}

## See also

An introduction to the OGC API specification

- https://ogcapi-workshop.ogc.org/

Example responses that comply with the specification

- https://github.com/opengeospatial/ogcapi-features/tree/master/core/examples
