# CRYT Python API

### Install dependencies
```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Test
```
poetry run pytest -v
```

### Build
```
poetry build
```

### Setup environment
```
export POETRY_PYPI_TOKEN_PYPI="token"
export POETRY_HTTP_BASIC_PYPI_USERNAME="username"
export POETRY_HTTP_BASIC_PYPI_PASSWORD="password"
```

### Update version
```
[tool.poetry]
version = "0.0.9"
```

### Publish
```
poetry publish
```
