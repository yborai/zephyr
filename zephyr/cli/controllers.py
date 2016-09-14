from cement.core.controller import CementBaseController, expose

class ZephyrCLI(CementBaseController):
    class Meta:
        label = "base"
        description = "The zephyr reporting toolkit"

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

__ALL__ = [ ZephyrCLI ]
