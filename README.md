# raypack

Raypack will create a package for AWS Glue, Ray.io tasks. This automates
this [documentation page](https://docs.aws.amazon.com/glue/latest/dg/edit-script-ray-env-dependencies.html) that has
some handwavy descriptions of shell commands. AWS Lambdas also call for a similar type of packaging, but as far as I 
know it is no sort of standard.

Use this if you have private dependencies, native dependencies, or you want to package your own code as a python
package. AWS Glue can't handle anything without a binary wheel or private package repositories, gcc or other build tools
are not in Glue runtime images.

See below for build options.

raypack is not supported by Amazon, AWS, nor Anyscale, Inc the makers of ray.io. Some code generate with ChatGPT (OpenAI)

![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/raypack) [![Downloads](https://pepy.tech/badge/raypack/month)](https://pepy.tech/project/raypack/month)

## Installation

You are encouraged to install with pipx so that the CLI tools dependencies do not conflict with your project
dependencies.

```shell
pipx install raypack
```

## Usage

```bash
raypack [--verbose]
```

```bash
python -m raypack  [--verbose]
```

Configuration. If none specified, defaults are as below.

```toml
[tool.raypack]
exclude_packaging_cruft = true
outer_folder_name = "venv"
source_venv = ".venv"
venv_tool = "poetry"
```


## Build Options

If your dependencies are all pure python, the packaging will work on any machine. However, if your dependencies have any native code:

Arm64 built on an Arm64 machine
- An actual arm64 build runner with gcc - Best option, will allow compiling native code correctly.
- Docker e.g. `FROM public.ecr.aws/lambda/python:3.9-arm64` - Second best option, I haven't tried it, not sure if it
  works on all build runners that are not actually arm64
  CPUs. [example](https://github.com/localstack-samples/multi-iac-devops/blob/11cd419c79758c2d33951fed8f8c72a1f78a68f5/devops-tooling/docker/Dockerfile.layer#L1)

Mac Binaries
- An arm64 machine e.g. mac - Next best option, not sure if it will work.

Precompiled Binaries
- Any machine or an arm64 machine like a mac- Would work in limited situations, namely when there are precompiled
  binaries (wheels) or all packages are pure python.

The last option works by telling pip to just download and unzip the arm64 wheels. If there aren't wheels or if the wheels
weren't compiled for arm64, then you have to consider finding a different machine or convincing package maintainers to support wheels and more kinds of wheels.

## Capabilities

- TODO: Warn if not python 3.9 or other glue compatible version
- TODO: create a venv for 3.9 if current venv is not 3.9
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

## How it works

On native arm64 machine
1. Gather info from pyproject.toml or CLI args, but not both.
2. Create a local .venv and .whl using poetry.
3. Create a new zip file with an extra top level folder.
4. Find the site-packages folder and copy to a new zip
5. Find the module contents in .whl and copy to a new zip
6. Upload to s3
7. Use s3 py modules `"--s3-py-modules", "s3://s3bucket/pythonPackage.zip"`

On non-arm64 machine
1. Use poetry lock file to generate requirements.txt
2. Use pip's download target with specified platform (arm64) to simulate creating a venv
3. Combine with own code as above
4. Upload to s3 as above

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