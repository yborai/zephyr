"""
The zephyr CLI entrypoint
"""
import os
import sys

from cement.core.foundation import CementApp
from cement.core.exc import FrameworkError
from cement.utils.misc import init_defaults

from .core.configure import CONFIG_PATH, CRED_ITEMS
from .core.utils import ZephyrException
from .cli.controllers import __ALL__ as ZephyrControllers
from .data.controllers import __ALL__ as ZephyrDataControllers
from .etl.controllers import __ALL__ as ZephyrETLControllers
from .report.controllers import __ALL__ as ZephyrReportControllers

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
        handlers = sum((
            ZephyrControllers,
            ZephyrDataControllers,
            ZephyrETLControllers,
            ZephyrReportControllers,
        ), [])
        extensions = [
            "zephyr.cli.output",
            "colorlog",
        ]
        output_handler = "default" # See .cli.output
        log_handler = "colorlog"

def main():
    with Zephyr() as app:
        for section, keys in CRED_ITEMS:
            for key in keys:
                env = os.environ.get(key)
                if env:
                    app.config.set(section, key, env)
        try:
            app.run()
        except ZephyrException as e:
            message = e.args[0]
            app.log.error(message)
            sys.exit(1)

if __name__ == "__main__":
    main()
