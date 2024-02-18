# PyTLS-CA

PyTLS-CA is a Python application that quickly creates self-signed TLS certificates for your local development environment.

## Install

You can install PyTLS-CA using pip:

```sh
pip install pytls-ca
```

## Usage

You can specify options like the CA name, the services for which to generate certificates, and the output directory. For example:

```sh
pytls -n 'My Custom CA' -s example.com -s api.example.com -d './certs'
```

## Options

- `-n`, `--ca-name`: The subject for the CA certificate. Defaults to `PyTLS CA`.
- `-s`, `--services`: The services for which to generate certificates. Can be specified multiple times for multiple services.
- `-d`, `--output-directory`: The directory in which to save the generated certificates. Defaults to `./certificates`.

# Development

This project uses [Poetry](https://python-poetry.org/) for dependency management. To install the project and its dependencies, run:

```sh
poetry install
```

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and code formatting.

### Publishing

To publish a new version of the package, run:

```sh
poetry config pypi-token.pypi <token>
poetry publish --build
```