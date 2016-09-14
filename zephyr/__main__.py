import os

from cement.core.foundation import CementApp
from cement.core.exc import FrameworkError
from cement.utils import fs, misc
from cement.utils.misc import init_defaults

from .cli.controllers import __ALL__ as ZephyrControllers
from .data.controllers import __ALL__ as ZephyrDataControllers
from .etl.controllers import __ALL__ as ZephyrETLControllers
from .report.controllers import __ALL__ as ZephyrReportControllers

defaults = init_defaults("zephyr", "log.logging")
defaults["log.logging"]["level"] = os.environ.get("ZEPHYR_DEBUG_LEVEL", "INFO")
defaults["log.colorlog"] = defaults["log.logging"]
defaults["zephyr"]["data_dir"] = "~/.zephyr"

class Zephyr(CementApp):
    class Meta:
        label = "zephyr"
        base_controller = "base"
        config_defaults = defaults
        handlers = sum((
            ZephyrControllers,
            ZephyrDataControllers,
            ZephyrETLControllers,
            ZephyrReportControllers,
        ), [])
        extensions = [
            "zephyr.cli.output",
            "colorlog",
            "mustache",
        ]
        output_handler = "mustache"
        log_handler = "colorlog"

def main():
    with Zephyr() as app:
        try:
            app.run()
        except FrameworkError as e:
            if not getattr(app.pargs, "output_handler_override", True):
                app.log.error("No output handler specified. Set with the -o flag.")
            raise e

if __name__ == "__main__":
    main()
