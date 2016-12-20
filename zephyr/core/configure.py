import io
import os
import sys

from .utils import ZephyrException

CONFIG_PATH = os.path.expanduser("~/.zephyr/config")
CRED_ITEMS = [
    (
        "lw-aws", [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "ZEPHYR_S3_BUCKET",
        ],
    ),
    (
        "lw-cc", [
            "CC_API_KEY",
            "CC_API_BASE",
        ],
    ),
    (
        "lw-dy", [
            "DY_HOST",
            "DY_USER",
            "DY_PASSWORD",
        ],
    ),
    (
        "lw-lo", [
            "LO_USER",
            "LO_PASSWORD",
        ],
    ),
    (
        "lw-sf", [
            "SF_USER",
            "SF_PASSWORD",
            "SF_TOKEN",
        ],
    ),
    (
        "zephyr", [
            "ZEPHYR_CACHE_ROOT",
            "ZEPHYR_DATABASE",
            "ZEPHYR_LINE_WIDTH",
        ],
    ),
]

def create_config(config, prompt=None, write=None, ini=None):
    if prompt:
        for section, keys in CRED_ITEMS:
            for key in keys:
                value = config.get(section, key, fallback="")
                user_input = input(
                    "{} [{}]: ".format(key, value)
                ) or value
                if(user_input == ""):
                    raise ZephyrException(
                        "This configuration item requires a value."
                    )
                config[section][key] = user_input

    out = io.StringIO()
    if write:
        ini = True
    for section in CRED_ITEMS:
        sec, keys = section
        if ini:
            out.write("[{}]\n".format(sec))
        for key in keys:
            out.write("{}={}\n".format(
                key, config.get(sec, key, fallback="")
            ))
    if write:
        print(CONFIG_PATH)
        with open(CONFIG_PATH, "w") as f:
            f.write(out.getvalue())
    print(out.getvalue(), end="")
    return config
