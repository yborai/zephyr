"""
The zephyr CLI entrypoint
"""
import os
import sys

from cement.core.foundation import CementApp
from cement.utils.misc import init_defaults

from .core.configure import CONFIG_PATH, CRED_ITEMS, DEFAULTS
from .core.utils import ZephyrException
from .cli.controllers import __ALL__ as ZephyrControllers

sections = tuple(zip(*CRED_ITEMS))[0] + ("log.logging",)
defaults = init_defaults(*sections)
defaults["log.logging"]["level"] = os.environ.get("ZEPHYR_DEBUG_LEVEL", "INFO")
defaults["log.colorlog"] = defaults["log.logging"]

class Zephyr(CementApp):
    class Meta:
        label = "zephyr"
        base_controller = "base"
        config_defaults = defaults
        config_files = [CONFIG_PATH]
        handlers = ZephyrControllers
        extensions = [
            "zephyr.cli.output",
            "colorlog",
        ]
        output_handler = "default" # See .cli.output
        log_handler = "colorlog"

    def configure(self):
        for section, keys in CRED_ITEMS:
            for key in keys:
                env = os.environ.get(key, DEFAULTS.get(key, ""))
                if env:
                    self.config.set(section, key, env)


def main():
    with Zephyr() as app:
        app.configure()
        try:
            app.run()
        except ZephyrException as e:
            message = e.args[0]
            app.log.error(message)
            sys.exit(1)


if __name__ == "__main__":
    main()
