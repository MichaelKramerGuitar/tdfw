# Local Setup

```bash
# install uv locally 
pip install uv
```

```bash
# use uv to manage your local virtual environment
uv venv
```

```powershell
# Activate the virtual environment
.venv\Scripts\Activate.ps1
```

```bash
# generate a lockfile from pyproject.toml
uv pip compile --group dev pyproject.toml -o uv.lock
```

```bash
# sync dependencies exactly as pinned in uv.lock
uv pip sync uv.lock
```

```bash
# install the package locally

# During development (editable)
uv pip install -e .

# When testing the built package (before publishing)
uv pip install .[dev]
```

```bash
# Test the install locally 

# Start a TouchDesigner App
tdfw start-app <MyFirstApp>

# Create a Python Extension stub
tdfw create-ext <MyFirstExt>
```


## Build the package
```bash
uv build
```

## Upload to PyPI

```bash
uv pip install twine

twine upload dist/*
```

## Verify Publish

search [pypi](https://pypi.org) for `tdfw`

## Then from some TouchDesigner Project location

```bash
uv pip install tdfw
```