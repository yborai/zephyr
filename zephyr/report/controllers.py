from cement.core.controller import CementBaseController, expose

class ZephyrReport(CementBaseController):
    class Meta:
        label = "report"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Generate advanced reports."
        parser_options = {}

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

class ZephyrAccountReview(ZephyrReport):
    class Meta:
        label = "account-review"
        stacked_on = "report"
        stacked_type = "nested"
        description = "Generate an account review for a given account."

        arguments = CementBaseController.Meta.arguments + [(
            ["--cache-folder"], dict(
                 type=str,
                 help="The path to the folder containing the  cached responses."
            )
        )]

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache_folder = self.app.pargs.cache_folder
        if(not cache_folder):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache_folder))

__ALL__ = [
    ZephyrReport,
    ZephyrAccountReview
]
