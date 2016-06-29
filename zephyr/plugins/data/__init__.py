from cement.core import handler, controller

from .ec2_details import ToolkitInstanceDetails

def load(app):
    handler.register(ToolkitInstanceDetails)
    handler.register(ToolkitDataController)

class ToolkitDataController(controller.CementBaseController):
    class Meta:
        label = 'data'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Generate single table reports for an account."
    
    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()
