from cement.core import handler, controller

def load(app):
    handler.register(ToolkitReportController)

class ToolkitReportController(controller.CementBaseController):
    class Meta:
        label = 'report'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Generate advanced reports."
    
    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()
