import xlsxwriter

from cement.core.controller import CementBaseController, expose

from ..core.cc.reports import (
    ReportRDS,
    ReportEC2,
    ReportMigration,
    ReportRIs,
)
from .common import formatting
from .underutil import underutil_xlsx
from .sr import ReportSRs

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

    def collate(self, sheets):
        account = self.app.pargs.account
        cache_file = self.app.pargs.cache_file
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        book_options = formatting["book_options"]
        filename = "{}.xlsx".format(self.Meta.label)
        with xlsxwriter.Workbook(filename, book_options) as book:
            out = self.reports(book, sheets, account, date, expire_cache, formatting)
        return out

    def reports(self, book, sheets, account, date, expire_cache, formatting):
        config = self.app.config
        log = self.app.log
        out = dict()
        for Sheet in sheets:
            out[Sheet] = Sheet(
                config,
                account=account,
                date=date,
                expire_cache=expire_cache,
                log=log,
            ).to_xlsx(book, formatting)
        return out

    def _run(self, *args):
        out = self.collate(args)
        sheet_set = {bool(value) for value in out.values()}
        if True not in sheet_set:
            self.app.log.info("No data to report!")

class ZephyrReportRun(ZephyrReport):
    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

class ZephyrAccountReview(ZephyrReportRun):
    class Meta:
        label = "account-review"
        stacked_on = "report"
        description = "Generate an account review for a given account."

    def run(self, **kwargs):
        self._run(
            ReportEC2,
            ReportRDS,
            ReportMigration,
            ReportRIs,
            ReportSRs,
        )

class ComputeDetailsReport(ZephyrReportRun):
    class Meta:
        label = "ec2"
        stacked_on = "report"
        description = "Generate the compute-details worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportEC2)

class ComputeMigrationReport(ZephyrReportRun):
    class Meta:
        label = "migration"
        stacked_on = "report"
        description = "Generate the compute-migration worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportMigration)

class ComputeRIReport(ZephyrReportRun):
    class Meta:
        label = "ri-recs"
        stacked_on = "report"
        description = "Generate the compute-ri worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportRIs)

class DBDetailsReport(ZephyrReportRun):
    class Meta:
        label = "rds"
        stacked_on = "report"
        description = "Generate the db-details worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportRDS)

class ComputeUnderutilizedReport(ZephyrReport):
    class Meta:
        label = "underutilized"
        stacked_on = "report"
        description = "Generate the compute-underutilized worksheet for a given account."

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache = self.app.pargs.cache_file
        if not cache:
            raise NotImplementedError
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            underutil = f.read()
        out = underutil_xlsx(json_string=underutil, formatting=formatting)
        if not out:
            self.app.log.info("No RI Recommendations to report!")

class ServiceRequestReport(ZephyrReportRun):
    class Meta:
        label = "sr"
        stacked_on = "report"
        description = "Generate the service-requests worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportSRs)

__ALL__ = [
    ZephyrReport,
    ZephyrAccountReview,
    ComputeDetailsReport,
    ComputeMigrationReport,
    ComputeRIReport,
    ComputeUnderutilizedReport,
    DBDetailsReport,
    ServiceRequestReport,
]
