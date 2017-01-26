import csv
import datetime
import os
import sys

import xlsxwriter

from shutil import copyfile

from cement.core.controller import CementBaseController, expose

from ..core import meta
from ..core.bd.calls import compute_av
from ..core.boto.calls import domains
from ..core.cc.calls import (
    BestPracticeChecksSummary,
    ComputeDetailsWarp,
    ComputeMigrationWarp,
    ComputeRIWarp,
    DBDetailsWarp,
    DBIdleWarp,
    IAMUsersData,
    LBIdleWarp,
    RIPricingWarp,
    StorageDetachedWarp,
)
from ..core.cc.client import CloudCheckr
from ..core.cc.reports import (
    ReportEC2,
    ReportMigration,
    ReportRDS,
    ReportRIs,
    ReportUnderutilized,
)
from ..core.configure import create_config
from ..core.client import Client
from ..core.ddh import DDH
from ..core.dy.calls import Billing
from ..core.dy.reports import ReportBilling
from ..core.lo.calls import ServiceRequests
from ..core.lo.reports import ReportSRs
from ..core.report import Report, ReportCoverPage
from ..core.utils import first_of_previous_month, ZephyrException

class ZephyrCLI(CementBaseController):
    class Meta:
        label = "base"
        description = "The zephyr reporting toolkit"

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

class ZephyrMeta(ZephyrCLI):
    class Meta:
        label = "meta"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Gather client meta information."
        arguments = CementBaseController.Meta.arguments + [(
            ["--expire-cache"], dict(
                action="store_true",
                help="Forces the cached data to be refreshed."
            )
        )]

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        config = self.app.config
        log = self.app.log
        self.ZEPHYR_LINE_WIDTH = int(self.app.config.get("zephyr", "ZEPHYR_LINE_WIDTH"))
        expire_cache = self.app.pargs.expire_cache
        self.app.log.info("Collecting client metadata.")
        projects = meta.LWProjects(config)
        projects.cache_policy(expire_cache, log=log)
        self.app.render(
            projects.get_all_projects(),
            line_width=self.ZEPHYR_LINE_WIDTH
        )

class ZephyrConfigure(ZephyrCLI):
    class Meta:
        label = "configure"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Gather configuration values."
        arguments = CementBaseController.Meta.arguments + [(
            ["--first-run"], dict(
                action="store_true",
                help=(
                    "Alias for --write --no-prompt."
                    " Initializes a configuration file with empty values."
                ),
            )
        ),
        (
            ["--ini"], dict(
                action="store_true",
                help="Include sections, as in INI format.",
            )
        ),
        (
            ["--no-prompt"], dict(
                action="store_true",
                help="Do not ask for values, but print given values."
            )
        ),
        (
            ["--write"], dict(
                action="store_true",
                help="Write configuration file. This option implies --ini."
            )
        )]


    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        first_run = self.app.pargs.first_run
        write = self.app.pargs.write or first_run # first_run implies write
        # first_run implies no prompt
        no_prompt = self.app.pargs.no_prompt or first_run
        prompt = not no_prompt
        ini = self.app.pargs.ini or write # write implies ini
        create_config(self.app.config, prompt, write, ini)

class ZephyrClearCache(ZephyrCLI):
    class Meta:
        label = "clear-cache"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Clears cache in S3 and locally for a given account and date."
        arguments = CementBaseController.Meta.arguments + [(
            ["--account"], dict(
                type=str,
                help="The desired account slug."
            ),
        ),
        (
            ["--date"], dict(
                type=str,
                help="The report date to request."
            ),
        ),
        (
            ["--all"], dict(
                action="store_true",
                help="Run for all accounts."
            )
        )]

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        config = self.app.config
        log = self.app.log
        account = self.app.pargs.account
        all_ = self.app.pargs.all
        date = self.app.pargs.date
        if not any((account, date, all_)):
            self.app.args.print_help()
            sys.exit()
        if not all((account, date)):
            raise ZephyrException("Account and date are required parameters.")

        month = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        client = Client(config)
        accts = client.get_slugs(all_) or [account]
        for acct in accts:
            if(not client.slug_valid(acct)):
                log.info("Skipping {}".format(acct))
                continue
            client.clear_cache_s3(acct, month, log)
            client.clear_cache_local(acct, month, log)

class ZephyrData(ZephyrCLI):
    class Meta:
        label = "data"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Generate single table reports for an account."
        arguments = CementBaseController.Meta.arguments + [(
            ["--account"], dict(
                 type=str,
                 help="The desired account slug."
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
        ),
        (
            ["--all"], dict(
                action="store_true",
                help="Run for all accounts."
            )
        )]

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

class DataRun(ZephyrData):
    class Meta:
        stacked_on = "data"
        stacked_type = "nested"
        arguments = ZephyrData.Meta.arguments

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run_call(self, cls, **kwargs):
        log = self.app.log
        account = self.app.pargs.account
        all_ = self.app.pargs.all
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        if not any((account, date, expire_cache, all_)):
            self.app.args.print_help()
            sys.exit()
        if not account:
            raise ZephyrException("Account is a required parameter.")
        client = cls(config=self.app.config, **kwargs)
        accts = client.get_slugs(all_) or [account]
        for acct in accts:
            if(not client.slug_valid(acct)):
                log.info("Skipping {}".format(acct))
                continue
            log.info("Running {report} for {account}".format(
                report=self.Meta.label,
                account=acct,
            ))
            try:
                response = client.cache_policy(
                    acct,
                    date,
                    expire_cache,
                    log=log,
                )
            except ZephyrException as e:
                message = e.args[0]
                log.error(message)
            client.parse(response)
            self.app.render(client.to_ddh())

class BillingLineItems(DataRun):
    class Meta:
        label = "billing-line-items"
        description = "Get the line items billing meta information."

    def run(self, **kwargs):
        self.run_call(Billing, **kwargs)

class BestPracticeChecksSummaryData(DataRun):
    class Meta:
        label = "bpc-summary"
        description = "Get a summary of the CloudCheckr best practice checks."

    def run(self, **kwargs):
        self.run_call(BestPracticeChecksSummary, **kwargs)

class ComputeDetails(DataRun):
    class Meta:
        label = "compute-details"
        description = "Get the detailed instance meta information."
        arguments = DataRun.Meta.arguments + [(
            ["--all-tags"], dict(
                 action="store_true",
                 help="Stores resource tag meta information in cell"
            )
        )]

    def run(self, **kwargs):
        kwargs["all_tags"] = self.app.pargs.all_tags
        self.run_call(ComputeDetailsWarp, **kwargs)

class ComputeMigration(DataRun):
    class Meta:
        label = "compute-migration"
        description = "Get the migration recommendations meta information"

    def run(self, **kwargs):
        self.run_call(ComputeMigrationWarp, **kwargs)

class ComputeRI(DataRun):
    class Meta:
        label = "compute-ri"
        description = "Get the ri recommendations meta information."

    def run(self, **kwargs):
        self.run_call(ComputeRIWarp, **kwargs)

class ComputeUnderutilized(DataRun):
    class Meta:
        label = "compute-underutilized"
        description = "Get the underutilized instances"

    def run(self, **kwargs):
        config = self.app.config
        log = self.app.log
        account = self.app.pargs.account
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache

        report = ReportUnderutilized(
            config,
            account,
            date,
            expire_cache,
            log,
        )
        cu_ddh = report.to_ddh()

        self.app.render(cu_ddh)

class DBDetails(DataRun):
    class Meta:
        label = "db-details"
        description = "Get the detailed rds meta information"

    def run(self, **kwargs):
        self.run_call(DBDetailsWarp, **kwargs)

class DBIdle(DataRun):
    class Meta:
        label = "db-idle"
        description = "List idle database instances."

    def run(self, **kwargs):
        self.run_call(DBIdleWarp, **kwargs)

class Domains(DataRun):
    class Meta:
        label = "domains"
        description = "List route-53 domains"

        arguments = DataRun.Meta.arguments + [(
            ["--access-key"], dict(
                type=str,
                help="The AWS Access Key ID for the desired client"
            )
        ), (
            ["--secret-key"], dict(
                type=str,
                help="The AWS Secret Access Key for the desired client"
            )
        ), (
            ["--session-token"], dict(
                type=str,
                help="The AWS Session Token for the desired client"
            )
        )]

    def run(self, **kwargs):
        access_key_id = self.app.pargs.access_key
        secret_key = self.app.pargs.secret_key
        session_token = self.app.pargs.session_token
        self.app.log.info("Checking for domains.")
        out = domains(access_key_id, secret_key, session_token)
        self.app.render(out)
        return out

class IAMUsers(DataRun):
    class Meta:
        label = "iam-users"
        description = "Get the IAM Users meta information"

    def run(self, **kwargs):
        self.run_call(IAMUsersData, **kwargs)

class LBIdle(DataRun):
    class Meta:
        label = "lb-idle"
        description = "List idle load balancers."

    def run(self, **kwargs):
        self.run_call(LBIdleWarp, **kwargs)

class RIPricings(DataRun):
    class Meta:
        label = "ri-pricings"
        description = "Get the detailed ri pricings meta information."

    def run(self, **kwargs):
        self.run_call(RIPricingWarp, **kwargs)

class ServiceRequestsRun(DataRun):
    class Meta:
        label = "service-requests"
        description = "get the detailed service requests meta information."

    def run(self, **kwargs):
        self.run_call(ServiceRequests, **kwargs)

class StorageDetached(DataRun):
    class Meta:
        label = "storage-detached"
        description = "List detached storage volumes."

    def run(self, **kwargs):
        self.run_call(StorageDetachedWarp, **kwargs)

class ComputeAV(DataRun):
    class Meta:
        label = "compute-av"
        description = "Get the AV of instance meta information"

        arguments = DataRun.Meta.arguments + [(
            ["--cache-file"], dict(
                 type=str,
                 help="The path to the cached response to use."
            )
        ),
        (
            ["--compute-details"], dict(
                type=str,
                help="The path to the cached compute-details response to use."
            )
        )]

    def run(self, **kwargs):
        cache_file = self.app.pargs.cache_file
        compute_details = self.app.pargs.compute_details
        if(not cache_file):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache_file))
        if(not compute_details):
            raise NotImplementedError
        self.app.log.info("Using compute_details response: {compute_details}".format(compute_details=compute_details))
        out = compute_av(cache_file, compute_details)
        self.app.render(out)
        return out

class ZephyrETL(CementBaseController):
    class Meta:
        label = "etl"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Perform Extract-Transform-Load operations on data."
        arguments = CementBaseController.Meta.arguments

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

class ZephyrDBRRI(ZephyrETL):
    class Meta:
        label = "dbr-ri"
        stacked_on = "etl"
        description = "Filter the DBR for only reserved instances."

        arguments = ZephyrETL.Meta.arguments + [
            (
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
                ),
            ),
        ]

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def filter_ri_dbr(self, infile, outfile, no_tags):
        with open(infile, "r") as dbrin, open(outfile, "w") as dbrout:
            reader = csv.DictReader(dbrin)
            header = reader.fieldnames
            if no_tags:
                header = [col for col in header if ":" not in col]
            print(header)
            writer = csv.DictWriter(dbrout, fieldnames=header, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for row in reader:
                if row["ReservedInstance"] != "Y":
                    continue
                out = {col:row[col] for col in header}
                writer.writerow(out)


    def run(self, **kwargs):
        infile = self.app.pargs.infile
        outfile = self.app.pargs.outfile
        no_tags = self.app.pargs.no_tags
        self.app.log.info("Using input file: {infile}".format(infile=infile))
        self.app.log.info("Using output file: {outfile}".format(outfile=outfile))
        self.filter_ri_dbr(infile, outfile, no_tags)

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
        ),
        (
            ["--all"], dict(
                action="store_true",
                help="Run for all accounts."
            )
        )]

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()

    def cache_key(self, slug, account, date):
        month = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        filename = "{slug}.xlsx".format(slug=slug)
        return os.path.join(account, month, filename)

    def collate(self, sheets, account, date, expire_cache, all_, log):
        config = self.app.config
        book_options = Report.formatting["book_options"]
        out = dict()
        client = Client(config)
        accts = client.get_slugs(all_) or [account]
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
                out = self.reports(book, sheets, acct, date, expire_cache)
            cache_key = self.cache_key(self.Meta.label, acct, date)
            cache_local = os.path.join(client.ZEPHYR_CACHE_ROOT, cache_key)
            copyfile(filename, cache_local)
            # Cache result to local cache and S3
            log.info(cache_local, cache_key)
            client.s3.meta.client.upload_file(
                cache_local, client.ZEPHYR_S3_BUCKET, cache_key
            )
        return out

    def reports(self, book, sheets, account, date, expire_cache):
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
                    log=log
                ).to_xlsx(book)
            except ZephyrException as e:
                message = e.args[0]
                log.error("Error in {sheet}: {message}".format(
                    sheet=Sheet.title, message=message
                ))
        return out

    def _run(self, *args):
        log = self.app.log
        account = self.app.pargs.account
        all_ = self.app.pargs.all
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        if not any((account, date, expire_cache, all_)):
            self.app.args.print_help()
            sys.exit()
        if not account:
            raise ZephyrException("Account is a required parameter.")
        # If no date is given then default to the first of last month.
        if(not date):
            date = first_of_previous_month().strftime("%Y-%m-%d")
        out = self.collate(args, account, date, expire_cache, all_, log)
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
            ReportCoverPage,
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
    BestPracticeChecksSummaryData,
    BillingLineItems,
    BillingReport,
    ComputeAV,
    ComputeDetails,
    ComputeDetailsReport,
    ComputeMigration,
    ComputeMigrationReport,
    ComputeRI,
    ComputeRIReport,
    ComputeUnderutilized,
    ComputeUnderutilizedReport,
    DBDetails,
    DBDetailsReport,
    DBIdle,
    Domains,
    IAMUsers,
    LBIdle,
    RIPricings,
    ServiceRequestReport,
    ServiceRequestsRun,
    StorageDetached,
    ZephyrAccountReview,
    ZephyrCLI,
    ZephyrConfigure,
    ZephyrClearCache,
    ZephyrData,
    ZephyrDBRRI,
    ZephyrETL,
    ZephyrMeta,
    ZephyrReport,
]
