# raypack

Raypack will create a package for AWS Glue, Ray.io tasks. This automates
this [documentation page](https://docs.aws.amazon.com/glue/latest/dg/edit-script-ray-env-dependencies.html) that has
some handwavy descriptions of shell commands.

If you are only using included-by-default packages, public packages, pure python packages,
binary wheel packages, you don't have to do this.

AWS Glue can't handle anything without a binary wheel or private package repositories, gcc or other build tools are not
in Glue runtime images.

See below for build options.

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

- TODO: Warn if not python 3.9 or other glue compatible version
- Calls poetry to create a virtualenv without dev dependencies
- TODO: support pip, pipenv to create virtualenv.
- Finds site-packages
- Zips virtualenv and zips own package
- TODO: support single file modules, eg. mymodule.py
- Skips cruft
- Run as few subprocesses as possible
- config using pyproject.toml or CLI args
- TODO: Uploads to s3
- pipx installable
- works on any OS as well as is possible (can't handle linux binaries on windows for example)
- Remove packages AWS includes
  - [AWS's documentation on packaging ray jobs](https://docs.aws.amazon.com/glue/latest/dg/edit-script-ray-env-dependencies.html) 
  - [ray's documentation on dependencies](https://docs.ray.io/en/latest/ray-core/handling-dependencies.html.
  - [AWS's documentation on packaging spark jobs](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-python-libraries.html) 

## Build Options

If your dependencies are all pure python, the packaging will work on any machine.

If your dependencies have any native code:

- An actual arm64 build runner - Best option, will allow compiling native code correctly.
- Docker e.g. `FROM public.ecr.aws/lambda/python:3.9-arm64` - Second best option, I haven't tried it, not sure if it works on all build runners that are not actually arm64 CPUs.
- An arm64 machine e.g. mac - Next best option, not sure if it will work.
- Any machine or an arm64 machine like a mac- Would work in limited situtions, namely when there are precomipiled binaries (wheels) or all packages are pure python.
 
## Usage

```bash
raypack
```

```bash
python -m raypack
```

Configuration. If none specified, defaults are as below.
```toml
[tool.raypack]
exclude_packaging_cruft = true
outer_folder_name = "venv"
source_venv = ".venv"
venv_tool = "poetry"
```

## How it works

1. Gather info from pyproject.toml or CLI args, but not both.
2. Create a local .venv and .whl using poetry.
3. Create a new zip file with an extra top level folder.
4. Find the site-packages folder and copy to a new zip
5. Find the module contents in .whl and copy to a new zip
6. Upload to s3
7. Use s3 py modules `"--s3-py-modules", "s3://s3bucket/pythonPackage.zip"`

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

[Some make file script](https://github.com/bhavintandel/py-packager)

Similar to PEX or other venv zip tools, which as far as I know are not AWS aware, or they don't include all the
dependencies, or they are more interested in making the archive file executable or self-extracting.

AWS Lambdas also have to go through a similar ad hoc zip process.

## Documentation

- [TODO](https://github.com/matthewdeanmartin/raypack/blob/main/docs/TODO.md)

## Change Log

- 0.1.0 - Idea and reserve package name.