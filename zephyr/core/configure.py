import os
import sys

from collections import OrderedDict

CREDS = OrderedDict(
    [
        (
            "cloudcheckr", [
                "api_key",
                "base"
            ]
        ),
        (
            "lw-aws", [
                "aws_access_key_id",
                "aws_secret_access_key",
                "s3_bucket"

            ]
        ),
        (
            "lw-dy", [
                "host",
                "user",
                "password"
            ]
        ),
        (
            "lw-lo", [
                "login",
                "passphrase"
            ]
        ),
        (
            "lw-sf", [
                "sf_username",
                "sf_passwd",
                "sf_token"
            ]
        ),
        (
            "tests", [
                "assets"
            ]
        ),
        (
            "zephyr", [
                "accounts",
                "cache",
                "database",
                "line_width"
            ]
        )
    ]
)

class Configure(object):
    def __init__(self):
        self.creds = CREDS

    def create_config(self, config):
        value = None
        for section, keys in self.creds.items():
            for key in keys:
                if key in config.keys(section):
                    value = config.get(section, key)
                user_input = input(
                    "What is your {} {}? [{}]: ".format(section, key, value)
                ) or value
                config[section][key] = user_input

        path = os.path.expanduser("~/.zephyr/config")
        with open(path, "w") as f:
            for section, keys in self.creds.items():
                f.write("[{}]\n".format(section))
                for key in keys:
                    value = config.get(section, key)
                    f.write(("{}={}\n".format(key, value)))
                f.write("\n")

        with open(path, "r") as f:
            for line in f:
                print(line, end="")

        return config
