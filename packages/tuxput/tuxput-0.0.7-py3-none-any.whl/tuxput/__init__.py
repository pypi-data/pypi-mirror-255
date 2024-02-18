# -*- coding: utf-8 -*-

from flask import (
    Flask,
    request,
)
from tuxput.resources import (
    s3_server,
    verify_bucket,
    verify_token,
    list_buckets,
)
from tuxput.config import TuxConfig
import json

__version__ = "0.0.7"


def create_app():
    app = Flask(
        __name__, instance_relative_config=True, static_folder="static"
    )

    config = TuxConfig()
    print("Setting auth_handler to {0}".format(config.CONF_BUCKET))
    auth_handler = s3_server(
        bucket=config.CONF_BUCKET, region=config.S3_REGION
    )

    @app.context_processor
    def add_site_name():
        return {"SITE_TITLE": config.SITE_TITLE}

    @app.context_processor
    def add_app_version():
        return {"VERSION": __version__}

    @app.route("/upload/<path:path>", methods=["POST"])
    def upload(path=""):
        """Attempt to upload an object."""
        token = request.headers.get("X-tuxput-token")
        requested_bucket = request.headers.get("X-tuxput-bucket")

        if path == "" or path == "/":
            return (
                "Forbidden: you must specify a key to upload the object",
                403,
            )

        # check that the bucket exists in our config
        # and get a TuxPutBucket obj
        bucket = verify_bucket(
            auth_handler, requested_bucket, config.CONF_FILE
        )
        if bucket is None:

            # if there's more than one bucket in the tuxput.json,
            # the user is required to specify a bucket.  If there's
            # only one, then verify_bucket will return it if
            # requested_bucket was None
            if requested_bucket is None:
                return ("Please specify a bucket to upload to", 404)

            # So, they asked for a bucket, we just don't have it.
            return (
                "Requested upload bucket not found '%s'" % requested_bucket,
                404,
            )

        # get user object by token
        user = verify_token(auth_handler, token, config.CONF_FILE)
        if user is None:
            return (
                "Token not found",
                401,
            )

        if not user.path_allowed(bucket.name, path):
            return (
                "Forbidden: token lacks write permission for"
                + "{0} on {1}\n".format(path, bucket.name),
                403,
            )

        # If still here, get ready to upload.
        real_path = bucket.real_path(path)
        print("real_path set to {0}".format(real_path))

        s3_handler = s3_server(bucket=bucket.name, region=config.S3_REGION)

        # If the url is to a specific object, check for overwrite perm.
        if s3_handler.key_exists(real_path):
            if not config.ALLOW_UPLOAD_OVERWRITE:
                return (
                    "Conflict: the key '{0}' already exists".format(path),
                    409,
                )

            # sneaky pete tried to overwrite the passwd file.. reuse previous
            # error
            if (
                real_path == config.CONF_FILE
                and bucket.name == config.CONF_BUCKET
            ):
                return (
                    "Permission denied for {0}".format(path),
                    403,
                )

        print(
            "Attempting to upload {0} as s3://{2}{1}".format(
                path, real_path, bucket.name
            )
        )
        return s3_handler.create_signed_url(real_path)

    @app.route("/buckets", defaults={"path": ""})
    def buckets_get(path):
        output = list_buckets(auth_handler, config.CONF_FILE)
        return json.dumps(output), 200

    @app.route("/authorizations", defaults={"path": ""})
    def authorizations_get(path):
        """Return the available authorized buckets and patterns for token"""
        token = request.headers.get("X-tuxput-token")

        # get user object by token
        user = verify_token(auth_handler, token, config.CONF_FILE)
        if user is None:
            return (
                "Token not found",
                401,
            )

        return json.dumps(user.authorizations), 200

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def default_get(path):
        return "Request refused, this site is for upload only\n", 200

    return app
