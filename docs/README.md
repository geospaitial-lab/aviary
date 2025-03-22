## Documentation

The documentation is built with [MkDocs] and the [Material for MkDocs] theme.<br />
The API reference is generated with [mkdocstrings-python].

The docs are built and deployed automatically on new releases with the [docs workflow].

  [MkDocs]: https://www.mkdocs.org
  [Material for MkDocs]: https://squidfunk.github.io/mkdocs-material
  [mkdocstrings-python]: https://mkdocstrings.github.io/python
  [docs workflow]: ../.github/workflows/docs.yaml

## Build the docs locally

Make sure you have the development dependencies installed:

```
pip install -r dev/requirements.txt
```

or:

```
uv pip install -r dev/requirements.txt
```

---

Build the maps:

```
python -m docs.scripts.build_maps
```

---

Build the docs:

```
mkdocs serve -f dev/mkdocs.yaml
```
