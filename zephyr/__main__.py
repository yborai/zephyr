import os

from cement.core import handler, controller, foundation, exc
from cement.utils.misc import init_defaults

defaults = init_defaults('zephyr', 'log.logging')
defaults['log.logging']['level'] = os.environ.get('ZEPHYR_DEBUG_LEVEL', 'INFO')
defaults['log.colorlog'] = defaults['log.logging']

class ToolkitBaseController(controller.CementBaseController):
    class Meta:
        label = 'base'
        description = "The zephyr reporting toolkit"
    
    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

class Toolkit(foundation.CementApp):
    class Meta:
        label = 'zephyr'
        base_controller = 'base'
        config_defaults = defaults
        plugins = [
            'configure',
            'data',
            'etl',
            'report',
            'stub',
        ]
        handlers = [
            ToolkitBaseController
        ]
        extensions = [
            'zephyr.plugins.data.output',
            'colorlog',
            'mustache',
        ]
        output_handler = 'mustache'
        log_handler = 'colorlog'

def main():
    with Toolkit() as app:
        try:
            app.run()
        except exc.FrameworkError as e:
            if not getattr(app.pargs, 'output_handler_override', True):
                app.log.error("No output handler specified. Set with the -o flag.")
            raise e

if __name__ == "__main__":
    main()
