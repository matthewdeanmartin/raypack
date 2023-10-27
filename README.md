# raypack

Raypack will create a package for AWS Glue, Ray.io tasks. This automates
this [documentation page](https://docs.aws.amazon.com/glue/latest/dg/edit-script-ray-env-dependencies.html) that has
some handwavy descriptions of shell commands.

If you are only using included-by-default packages, public packages, pure python packages,
binary wheel packages, you don't have to do this.

AWS Glue can't handle anything without a binary wheel or private package repositories, gcc or other build tools are not
in Glue runtime images.

So you have build on a machine that matches the AWS runtime OS (Fedora-like), create a virtual directory,
and then zip it up and upload it to s3.

This tool aims to do that and be pipx installable and work on any OS

Some code generate with ChatGPT (OpenAI)

raypack is not supported by Amazon, AWS, nor Anyscale, Inc the makers of ray.io.

![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/raypack) [![Downloads](https://pepy.tech/badge/raypack/month)](https://pepy.tech/project/raypack/month)

## Installation

You are encouraged to install with pipx so that the CLI tools dependencies do not conflict with your project
dependencies.

```shell
pipx install raypack
```

## Capabilities

- Finds site-packages
- Zips files
- Skips cruft.
- Uploads to s3
- No dependencies on shell or subprocess (yet)
- config using pyproject.toml or CLI args

## Not Supported

- Calling pip, poetry, pipenv to create virtualenv.

## Usage

```bash
python -m raypack
```

```bash
raypack
```
## Contributing

To install and run tests and linting tools.
```bash
poetry install --with dev
make check
```

To see if the app can package up other apps
```bash
poetry build
# exist poetry shell so that pipx can install with the right base python
exit 
pipx install /e/github/raypack/dist/raypack-0.1.0-py3-none-any.whl
```
And then in a different project with a `pyproject.toml` file, run

```bash
raypack
```

## Prior Art

[Random scripts in comments](https://github.com/python-poetry/poetry/issues/1937#issuecomment-983754739)

Similar to PEX or other venv zip tools, which as far as I know are not AWS aware, or they don't include all the
dependencies, or they are more interested in making the archive file executable or self-extracting.

## Documentation

- [TODO](https://github.com/matthewdeanmartin/raypack/blob/main/docs/TODO.md)

## Change Log

- 0.1.0 - Idea and reserve package name.