"""
The zephyr CLI entrypoint
"""
import os

from cement.core.foundation import CementApp
from cement.core.exc import FrameworkError
from cement.utils.misc import init_defaults

from .cli.controllers import __ALL__ as ZephyrControllers
from .data.controllers import __ALL__ as ZephyrDataControllers
from .etl.controllers import __ALL__ as ZephyrETLControllers
from .report.controllers import __ALL__ as ZephyrReportControllers

defaults = init_defaults(
    "aws",
    "cloudcheckr",
    "log.logging",
    "lw-aws",
    "lw-sf",
    "tests",
    "zephyr",
)
defaults["log.logging"]["level"] = os.environ.get("ZEPHYR_DEBUG_LEVEL", "INFO")
defaults["log.colorlog"] = defaults["log.logging"]
defaults["aws"]["AWS_ACCESS_KEY_ID"] = os.environ.get("AWS_ACCESS_KEY_ID")
defaults["aws"]["AWS_SECRET_ACCESS_KEY"] = os.environ.get("AWS_SECRET_ACCESS_KEY")
defaults["aws"]["AWS_SECURITY_TOKEN"] = os.environ.get("AWS_SECURITY_TOKEN")
defaults["aws"]["AWS_SESSION_TOKEN"] = os.environ.get("AWS_SESSION_TOKEN")

class Zephyr(CementApp):
    class Meta:
        label = "zephyr"
        arguments_override_config = True
        base_controller = "base"
        config_defaults = defaults
        config_files = [
            "~/.aws/config",
            "~/.zephyr/config",
        ]
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
        try:
            app.args.add_argument('--line_width', action='store', dest='line_width')
            app.run()
        except FrameworkError as e:
            raise e

if __name__ == "__main__":
    main()
