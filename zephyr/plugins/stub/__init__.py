from cement.core import handler, controller

def load(app):
    from . import echo
    
    handler.register(echo.ToolkitEcho)
    handler.register(ToolkitStubController)

class ToolkitStubController(controller.CementBaseController):
    class Meta:
        label = 'stub'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "a test plugin"
    
    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()
