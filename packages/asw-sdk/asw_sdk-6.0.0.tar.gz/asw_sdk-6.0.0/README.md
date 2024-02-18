# Sample ENV variable

## Steps to create a new version

- update version in setup.py

```bash
pip install twine
```

```bash
python setup.py sdist
```

for `pypitest`


```bash
twine upload --repository testpypi dist/*
```

for `pypi`

```bash
twine upload dist/*
```

