from cement.core.controller import CementBaseController, expose

from . import account_review
from .service_requests import service_request_xlsx

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

class ServiceRequestReport(ZephyrReport):
    class Meta:
        label = "sr-report"
        stacked_on = "report"
        stacked_type = "nested"
        description = "Generate the service-requests worksheet for a given account."

        arguments = CementBaseController.Meta.arguments + [(
            ["--cache"], dict(
                type=str,
                help="The path to the json cached file."
            )
        )]

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if not cache:
            raise NotImplementedError
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            srs = f.read()
        service_request_xlsx(srs)



__ALL__ = [
    ZephyrReport,
    ZephyrAccountReview,
    ServiceRequestReport
]
