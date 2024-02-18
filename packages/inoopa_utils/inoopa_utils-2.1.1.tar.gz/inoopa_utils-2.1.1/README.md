# Inoopa's helpers

This repo contains helper functions we use in all of our python projects.

## This is pushed publicly to Pypi, so NEVER commit any secret here

## How to use this package in your code
```bash
pip install inoopa_utils
```

## How to publish package to Pypi

After any code change, **update the package version** in [pyproject.toml](./pyproject.toml).

Then, at the root of the repo:

```bash
# Login to Pypi
poetry config pypi-token.pypi <Pypi API token here>

# Build project
poetry build

# Publish
poetry publish
```

## Docker image
This repo's ci/cd is building an image stored at `inoopa/python311`. 
This is because inoopa_utils uses [deepparse](https://github.com/GRAAL-Research/deepparse) which requires Pytorch and some others dependencies.

Those are long to install in a docker image, which enventually reflect on our bills. 
To avoid this, we build the image once and build other images on top of it.