from cement.core.controller import CementBaseController, expose

from ..data.service_requests import ServiceRequests
from .common import formatting
from .ec2 import ec2_xlsx
from .rds import rds_xlsx
from .ri_recs import ri_xlsx
from .sr import sr_xlsx

class ZephyrReport(CementBaseController):
    class Meta:
        label = "report"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Generate advanced reports."
        parser_options = {}
        arguments = CementBaseController.Meta.arguments + [(
            ["--account"], dict(
                 type=str,
                 help="The desired account slug."
            )
        ),
        (
            ["--cache-file"], dict(
                type=str,
                help="The path to the json cached file."
            )
        ),
        (
            ["--expire-cache"], dict(
                action="store_true",
                help="Forces the cached data to be refreshed."
            )
        )]

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
        cache_folder = self.app.pargs.cache_file_folder
        if(not cache_folder):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache_folder))

class ComputeDetailsReport(ZephyrReport):
    class Meta:
        label = "ec2"
        stacked_on = "report"
        stacked_type = "nested"
        description = "Generate the compute-details worksheet for a given account."

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache = self.app.pargs.cache_file
        if not cache:
            raise NotImplementedError
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            ec2 = f.read()
        ec2_xlsx(json_string=ec2, formatting=formatting)

class DBDetailsReport(ZephyrReport):
    class Meta:
        label = "rds"
        stacked_on = "report"
        stacked_type = "nested"
        description = "Generate the db-details worksheet for a given account."

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache = self.app.pargs.cache_file
        if not cache:
            raise NotImplementedError
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            rds = f.read()
        rds_xlsx(json_string=rds, formatting=formatting)

class ComputeRIReport(ZephyrReport):
    class Meta:
        label = "ri-recs"
        stacked_on = "report"
        stacked_type = "nested"
        description = "Generate the compute-ri worksheet for a given account."

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache = self.app.pargs.cache_file
        if not cache:
            raise NotImplementedError
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            ri = f.read()
        ri_xlsx(json_string=ri, formatting=formatting)

class ServiceRequestReport(ZephyrReport):
    class Meta:
        label = "sr"
        stacked_on = "report"
        stacked_type = "nested"
        description = "Generate the service-requests worksheet for a given account."
        arguments = ZephyrReport.Meta.arguments + [(
            ["--date"], dict(
                 type=str,
                 help="The report date to request."
            )
        )]


    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        account = self.app.pargs.account
        cache = self.app.pargs.cache_file
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        response = ServiceRequests.cache(
            account, date, cache, expire_cache, config=self.app.config, log=self.app.log
        )
        sr_xlsx(json_string=response, formatting=formatting)


__ALL__ = [
    ZephyrReport,
    ZephyrAccountReview,
    ComputeDetailsReport,
    ComputeRIReport,
    DBDetailsReport,
    ServiceRequestReport,
]
