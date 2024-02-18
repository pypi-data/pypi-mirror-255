# OGC API Test Client

A black box verifier for OGC API specifications


## Installation
This package is available on PyPi and can be installed with pip

```bash
$ python -m pip install ogctests
```

## Usage
The test suite is designed to be run from the command line. At least one scope and an instance URL must be provided.

```bash
$ python -m ogctests <scope_1> [<scope_2>] -i <instance_url>
```

for instructions on how to scope the tests, call the package with  the `-h` flag.

```bash
$ python -m ogctests -h
```

## Reporting

Currently the test suite only outputs a brief summary of passes and failures from pytest.  
In the future a proper report will be produced after each test session.

> **Note**: Reporting not yet implemented.


## What it Does

In line with the
[Official OGC test suite](https://github.com/opengeospatial/ets-ogcapi-features10)
(written in Java), this Python-based test suite will verify the compliance of a
given endpoint with the
[OGC API - Features - Part 1: Core](https://docs.ogc.org/is/17-069r3/17-069r3.html)
specification.

The test suite only tests against the **OGC API - Features - Part 1:
Core** specification, But may be expanded in the future.

## See also

**An introduction to the OGC API specification**
- https://ogcapi-workshop.ogc.org/

**OGC API — Features — Part 1: Core**
- https://docs.ogc.org/is/17-069r3/17-069r3.html

**Official OGC test suite**
- https://github.com/opengeospatial/ets-ogcapi-features10

### Implementors

- https://demo.pygeoapi.io/stable
- https://demo.ldproxy.net/vineyards
- https://demo.ldproxy.net/daraa
- https://demo.ldproxy.net/zoomstack
- https://www.ldproxy.nrw.de/kataster
