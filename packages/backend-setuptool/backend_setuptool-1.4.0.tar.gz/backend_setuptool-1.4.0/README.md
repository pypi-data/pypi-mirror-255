# Packaging using setuptool

## Upgrading build

    python -m pip install --upgrade build

## Build the package

    python -m build

## Package versioning

    python -m pip install bumpver
    bumpver init
    bumpver update --minor

## Add Resource Files to Your Package

    include src/reader/*.toml

## License Your Package

## Install Your Package Locally

    python -m pip install -e .

## Uploading the distribution archives

    python -m pip install --upgrade twine
    python -m twine upload --repository testpypi dist/*

## Installing your newly uploaded package

    python -m pip install --index-url https://test.pypi.org/simple/ --no-deps backend_setuptool
