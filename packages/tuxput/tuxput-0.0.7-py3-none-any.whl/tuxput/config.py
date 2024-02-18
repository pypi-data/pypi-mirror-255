# -*- coding: utf-8 -*-

import os
from distutils.util import strtobool


class TuxConfig:
    def __init__(self):
        self.config_strings = {}
        self.config_strings["S3_REGION"] = None
        self.config_strings["CONF_BUCKET"] = None
        self.config_strings["CONF_FILE"] = "tuxput.json"

        self.config_bools = {}
        self.config_bools["ALLOW_UPLOAD_OVERWRITE"] = False
        for config_var in self.config_bools:
            if config_var in os.environ:
                self.config_bools[config_var] = bool(
                    strtobool(os.environ[config_var])
                )

        for config_var in self.config_strings:
            if config_var in os.environ:
                self.config_strings[config_var] = os.environ[config_var]

        assert (
            self.config_strings["CONF_FILE"] is not None
        ), "Required env var CONF_FILE not set"
        assert (
            self.config_strings["CONF_BUCKET"] is not None
        ), "Required env var CONF_BUCKET not set"
        assert (
            self.config_strings["S3_REGION"] is not None
        ), "Required env var S3_REGION not set"

    @property
    def S3_REGION(self):
        return self.config_strings["S3_REGION"]

    @property
    def SITE_TITLE(self):
        return self.config_strings["SITE_TITLE"]

    @property
    def ALLOW_UPLOAD_OVERWRITE(self):
        return self.config_bools["ALLOW_UPLOAD_OVERWRITE"]

    @property
    def CONF_BUCKET(self):
        return self.config_strings["CONF_BUCKET"]

    @property
    def CONF_FILE(self):
        return self.config_strings["CONF_FILE"]
