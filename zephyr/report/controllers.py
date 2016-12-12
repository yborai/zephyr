import xlsxwriter

from cement.core.controller import CementBaseController, expose

from ..core.client import Client
from ..core.utils import ZephyrException
from ..core.cc.client import CloudCheckr
from ..core.cc.reports import (
    ReportEC2,
    ReportMigration,
    ReportRDS,
    ReportRIs,
    ReportUnderutilized,
)
from ..core.dy.reports import ReportBilling
from .common import formatting
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
                 help=(
                    "The desired account slug. The value 'all' will iterate"
                    " through all available slugs."
                )
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
        log = self.app.log
        account = self.app.pargs.account
        cache_file = self.app.pargs.cache_file
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        book_options = formatting["book_options"]
        accts = [account]
        out = dict()
        if(account == "all"):
            accts = Client(self.app.config).get_slugs()
        for acct in accts:
            if(not self.slug_valid(acct)):
                log.info("Skipping {}".format(acct))
                continue
            log.info("Running {report} for {account}".format(
                report=self.Meta.label,
                account=acct,
            ))
            filename = "{slug}.{label}.xlsx".format(
                label=self.Meta.label, slug=acct
            )
            with xlsxwriter.Workbook(filename, book_options) as book:
                out = self.reports(
                    book, sheets, acct, date, expire_cache, formatting
                )
        return out

    def reports(self, book, sheets, account, date, expire_cache, formatting):
        config = self.app.config
        log = self.app.log
        out = dict()
        for Sheet in sheets:
            try:
                out[Sheet] = Sheet(
                    config,
                    account=account,
                    date=date,
                    expire_cache=expire_cache,
                    log=log,
                ).to_xlsx(book, formatting)
            except ZephyrException as e:
                message = e.args[0]
                log.error("Error in {sheet}: {message}".format(
                    sheet=Sheet.title, message=message
                ))
        return out

    def _run(self, *args):
        out = self.collate(args)
        sheet_set = {bool(value) for value in out.values()}
        if True not in sheet_set:
            self.app.log.info("No data to report!")

class ZephyrReportRun(ZephyrReport):
    class Meta:
        stacked_on = "report"

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def slug_valid(self, slug):
        return True

class ZephyrAccountReview(ZephyrReportRun):
    class Meta:
        label = "account-review"
        description = "Generate an account review for a given account."

    def run(self, **kwargs):
        self._run(
            ReportBilling,
            ReportEC2,
            ReportRDS,
            ReportMigration,
            ReportRIs,
            ReportSRs,
            ReportUnderutilized,
        )

    def slug_valid(self, slug):
        client = CloudCheckr(config=self.app.config)
        return client.get_account_by_slug(slug)

class BillingReport(ZephyrReportRun):
    class Meta:
        label = "billing"
        description = "Generate the compute-details worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportBilling)

class ComputeDetailsReport(ZephyrReportRun):
    class Meta:
        label = "ec2"
        description = "Generate the compute-details worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportEC2)

class ComputeMigrationReport(ZephyrReportRun):
    class Meta:
        label = "migration"
        description = "Generate the compute-migration worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportMigration)

class ComputeRIReport(ZephyrReportRun):
    class Meta:
        label = "ri-recs"
        description = "Generate the compute-ri worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportRIs)

class DBDetailsReport(ZephyrReportRun):
    class Meta:
        label = "rds"
        description = "Generate the db-details worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportRDS)

class ComputeUnderutilizedReport(ZephyrReportRun):
    class Meta:
        label = "underutilized"
        description = "Generate the compute-underutilized worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportUnderutilized)

class ServiceRequestReport(ZephyrReportRun):
    class Meta:
        label = "sr"
        description = "Generate the service-requests worksheet for a given account."

    def run(self, **kwargs):
        self._run(ReportSRs)

__ALL__ = [
    ZephyrReport,
    ZephyrAccountReview,
    BillingReport,
    ComputeDetailsReport,
    ComputeMigrationReport,
    ComputeRIReport,
    ComputeUnderutilizedReport,
    DBDetailsReport,
    ServiceRequestReport,
]
