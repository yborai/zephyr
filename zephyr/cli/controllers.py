from cement.core.controller import CementBaseController, expose

class ZephyrCLI(CementBaseController):
    class Meta:
        label = "base"
        description = "The zephyr reporting toolkit"
    
    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

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

class ZephyrData(CementBaseController):
    class Meta:
        label = "data"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Generate single table reports for an account."
        arguments = CementBaseController.Meta.arguments + [(
            ["--config"], dict(
                type=str,
                help="Path to configuration file"
            )
        ), (
            ["--cache"], dict(
                 type=str,
                 help="The path to the cached response to use."
            )
        ), (
            ["--compute_details"], dict(
                type=str,
                help="The path to the cached compute-details response to use."
            )
        )]

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

class ZephyrETL(CementBaseController):
    class Meta:
        label = "etl"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Generate single table reports for an account."
        arguments = CementBaseController.Meta.arguments + [(
                ["--infile"], dict(
                    type=str,
                    help="Path to input file.",
                    required=True,
                ),
            ),
            (
                ["--outfile"], dict(
                    type=str,
                    help="Path to output file.",
                    required=True,
                ),
            ),
            (
               ["--no-tags"], dict(
                    action="store_true",
                    help="Removes tags in output file."
                )
        )]

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

