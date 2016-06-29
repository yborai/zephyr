from cement.core import controller

class ToolkitEcho(controller.CementBaseController):
    class Meta:
        label = 'echo'
        stacked_on = 'stub'
        stacked_type = 'nested'
        description = "Echo a message."
        
        # These args will only be added to this subcommand, but include the default args
        # The format is identical to the standard library argparse module
        arguments = controller.CementBaseController.Meta.arguments + [(
            ['--message'], dict(
                type=str,
                help='The message to echo.'
            )
        )]
    
    @controller.expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))
    
    def run(self, **kwargs):
        msg = self.app.pargs.message
        self.app.log.info("Echo: {msg}".format(msg=msg))
        self.app.render(
            dict(message=msg),
        )
