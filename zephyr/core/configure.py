import io
import os

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
DEFAULTS = {
    "ZEPHYR_CACHE_ROOT": os.path.expanduser("~/.zephyr/cache/"),
    "ZEPHYR_DATABASE": ".meta/local.db",
}

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
    for section in CRED_ITEMS:
        sec, keys = section
        if ini:
            out.write("[{}]\n".format(sec))
        for key in keys:
            out.write("{}={}\n".format(
                key, config.get(sec, key, fallback="")
            ))
    if write:
        cache_root = os.path.expanduser(config.get(
            "zephyr",
            "ZEPHYR_CACHE_ROOT",
            fallback=DEFAULTS["ZEPHYR_CACHE_ROOT"]
        ))
        db = config.get(
            "zephyr", "ZEPHYR_DATABASE", fallback=DEFAULTS["ZEPHYR_DATABASE"]
        )
        db_dir = os.path.dirname(os.path.join(cache_root, db))
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        os.makedirs(db_dir, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            f.write(out.getvalue())
    print(out.getvalue(), end="")
    return config
