## Tests

The tests are based on [pytest](https://docs.pytest.org)
and [pytest-cov](https://pytest-cov.readthedocs.io).

## Run the tests locally

Make sure you have the development dependencies installed:

```
pip install -r dev/requirements.txt
```

or:

```
uv pip install -r dev/requirements.txt
```

Run the tests:

```
pytest
```

Run the tests with coverage:

```
pytest --cov
```
