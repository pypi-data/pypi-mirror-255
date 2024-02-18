# snippets-yw

## Hacking 

```bash
pip install --editable .
```

build & publish 

```bash
python3 -m build && \
python3 -m twine upload --repository pypi dist/* --verbose
```

