from cement.core.controller import CementBaseController, expose

from ..data.compute_details import ComputeDetailsWarp
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
            ["--date"], dict(
                 type=str,
                 help="The report date to request."
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
        description = "Generate an account review for a given account."

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        # TODO: Combine working reports here.
        raise NotImplementedError

class ComputeDetailsReport(ZephyrReport):
    class Meta:
        label = "ec2"
        stacked_on = "report"
        description = "Generate the compute-details worksheet for a given account."

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        account = self.app.pargs.account
        cache_file = self.app.pargs.cache_file
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        client = ComputeDetailsWarp(config=self.app.config)
        response = client.cache_policy(
            account, date, cache_file, expire_cache, log=self.app.log
        )
        client.parse(response)
        out = ec2_xlsx(client=client, formatting=formatting)
        if not out:
            self.app.log.info("No Compute Instances to report!")

class DBDetailsReport(ZephyrReport):
    class Meta:
        label = "rds"
        stacked_on = "report"
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
        out = rds_xlsx(json_string=rds, formatting=formatting)
        if not out:
            self.app.log.info("No RDS Instances to report!")

class ComputeMigrationReport(ZephyrReport):
    class Meta:
        label = "migration"
        stacked_on = "report"
        description = "Generate the compute-migration worksheet for a given account."

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache = self.app.pargs.cache_file
        if not cache:
            raise NotImplementedError
        self.app.log.info("using cached response:{cache}".format(cache=cache))
        with open(cache, "r") as f:
            migr = f.read()
        out = migration_xlsx(json_string=migr, formatting=formatting)
        if not out:
            self.app.log.info("No Migration to report!")

class ComputeRIReport(ZephyrReport):
    class Meta:
        label = "ri-recs"
        stacked_on = "report"
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
        out = ri_xlsx(json_string=ri, formatting=formatting)
        if not out:
            self.app.log.info("No RI Recommendations to report!")

class ServiceRequestReport(ZephyrReport):
    class Meta:
        label = "sr"
        stacked_on = "report"
        description = "Generate the service-requests worksheet for a given account."

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        account = self.app.pargs.account
        cache_file = self.app.pargs.cache_file
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        client = ServiceRequests(config=self.app.config)
        response = client.cache_policy(
            account, date, cache_file, expire_cache, log=self.app.log
        )
        out = sr_xlsx(json_string=response, formatting=formatting)
        if not out:
            self.app.log.info("No Service Requests to report!")

__ALL__ = [
    ZephyrReport,
    ZephyrAccountReview,
    ComputeDetailsReport,
    ComputeRIReport,
    DBDetailsReport,
    ServiceRequestReport,
]
