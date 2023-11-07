# TODO

Everything!

- unit tests - 25% done
- moto tests - TODO
- s3 upload - TODO
- toml config - mostly done
- CLI args - TODO
- testing with actual AWS Glue
- gitlab actions - mostly done
- tox - done?
- try out https://github.com/gruns/icecream

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

- pipx installable
- works on any OS as well as is possible (can't handle linux binaries on windows for example)
- Remove packages AWS includes
    - [AWS's documentation on packaging ray jobs](https://docs.aws.amazon.com/glue/latest/dg/edit-script-ray-env-dependencies.html)
    - [ray's documentation on dependencies](https://docs.ray.io/en/latest/ray-core/handling-dependencies.html.
    - [AWS's documentation on packaging spark jobs](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-python-libraries.html)


## Deployment
- Upload zip to s3, e.g. "glue-python-packages"
- Upload entrypoint script to s3, e.g. "aws-glue-assets-{account_number}-us-east-1"
- Update job to point to new script (if name is new)
  - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue/client/update_job.html

## TODO
- support people who don't use private repos (use only pip/requirement.txt)
- setup dev environment that matches glue machine (which has specific binary versions)