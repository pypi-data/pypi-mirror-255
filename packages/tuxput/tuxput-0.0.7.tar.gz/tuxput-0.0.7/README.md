# tuxput

[![PyPI version](https://badge.fury.io/py/tuxput.svg)](https://pypi.org/project/tuxput/)

The Serverless File Uploader

tuxput is a python/flask application which provides a file uploading interface
to S3, and is designed to be run serverlessly with
[Zappa](https://github.com/Miserlou/Zappa).

# Configuration

Configuration is handled by a JSON file stored in S3 and some
environment variables that must be set in order to access it.

# Environment Variables

The following configuration variables should be set when running
tuxput:


- `CONF_BUCKET`
  - required: True
  - description: S3 bucket name containing the configuration. Example:
    `testing-tuxput-auth`
- `CONF_FILE`
  - required: False
  - description: String that is the key (filename) of a json file containing
    user with access and the buckets to which they may upload.  Defaults to
    'tuxput.json'
- `S3_REGION`
  - required: True
  - description: Region containing the S3 bucket. Example:`us-east-1`
- `SITE_TITLE`
  - required: False
  - description: Defaults to `Tuxput`. Set to anything you like for a global
    site title.
- `ALLOW_UPLOAD_OVERWRITE`
  - required: False
  - description: boolean, defaults to False.  Allows uploaders to overwrite
    existing files.

# JSON Configuration

The `CONF_FILE` provides configuration information for buckets that are
served and the users that may access them.  An example may be found in
the file `sample-tuxput.json`.  There are two top level JSON objects that
are listed here:  buckets and users

## buckets

"buckets" is a list of dicts consisting of:

name           : The name of the bucket in S3
root (optional): Specifies an offset directory from the root of the S3 share.

If not "root" setting is available for the bucket, then tuxput assumes that 
"/" is the root.

## users

"users" is a list of dicts describing the users that are allowed to upload
to the server.  The only two required options are:

token          : The token that is used to identify the user
authorizations : a list of authorizations for the user

"authorizations" are made up of:

bucket          : a pattern to match for the name of the S3 bucket for which
                  the authorization rule applies
restricted_paths: a list path patterns where the user is allowed to upload
                  (will default to "*" and grant full access if not specified)

Any other fields in the file are ignored, but may be used to record 
administratively interesting information (ie, username or email assocaited
with the token, when the token was created, etc).


# Run Locally

To run locally, install tuxput, ensure AWS access is available environmentally,
and run:

```shell
CONF_BUCKET=testing-tuxput-auth S3_REGION=us-east-1 FLASK_APP=tuxput flask run
```

# Run with Zappa

This application is intended to be ran and deployed with
[Zappa](https://github.com/Miserlou/Zappa) and hosted by AWS [API
Gateway](https://aws.amazon.com/api-gateway/) and
[Lambda](https://aws.amazon.com/lambda/).

To use with Zappa, create an app shim named zappa_init.py:

```python
# When using a flask app factory, this file is required.
# See https://github.com/Miserlou/Zappa/issues/1771
# and https://github.com/Miserlou/Zappa/pull/1775
from tuxpub import create_app
app = create_app()
```

An example zappa_settings.yaml file may look like:
```yaml
{
---
prod:
  app_function: zappa_init.app
  aws_region: us-east-1
  project_name: testing-tuxput
  runtime: python3.7
  s3_bucket: testing-tuxput
  domain: testing-tuxput.ctt.linaro.org
  certificate_arn: arn:aws:acm:us-east-1:49557002050:certificate/92772d7-0d15-48d1-a707-010ec561c10
  environment_variables:
    CONF_BUCKET: testing-tuxput-auth
    S3_REGION: us-east-1
```
