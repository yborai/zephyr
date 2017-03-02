import csv
import datetime
import sys

from cement.core.controller import CementBaseController, expose

from ..core import meta
from ..core.book import Book
from ..core.client import Client
from ..core.configure import create_config
from ..core.sheet import CoverPage
from ..core.utils import first_of_previous_month, ZephyrException
from ..core.bd.calls import compute_av
from ..core.boto.calls import domains
from ..core.cc.sheets import (
    SheetDBIdle,
    SheetEC2,
    SheetIAMUsers,
    SheetLBIdle,
    SheetMigration,
    SheetRDS,
    SheetRIs,
    SheetStorageDetached,
    SheetUnderutilized,
)
from ..core.dy.sheets import SheetBilling
from ..core.lo.sheets import SheetSRs

class ZephyrCLI(CementBaseController):
    class Meta:
        label = "base"
        description = "The zephyr reporting toolkit"
        arguments = CementBaseController.Meta.arguments

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()
        sys.exit(0)

class ZephyrCall(ZephyrCLI):
    class Meta:
        arguments = ZephyrCLI.Meta.arguments + [(
            ["--account"], dict(
                 type=str,
                 help="The desired account slug."
            )
        ),
        (
            ["--all"], dict(
                action="store_true",
                help="Run for all accounts."
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

class ZephyrClearCache(ZephyrCLI):
    class Meta:
        label = "clear-cache"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Clears cache in S3 and locally for a given account and date."
        arguments = ZephyrCLI.Meta.arguments + [(
            ["--account"], dict(
                type=str,
                help="The desired account slug."
            ),
        ),
        (
            ["--all"], dict(
                action="store_true",
                help="Run for all accounts."
            )
        ),
        (
            ["--date"], dict(
                type=str,
                help="The report date to request."
            ),
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
            sys.exit(0)
        if not (date and any((account, all_))):
            raise ZephyrException("Account and date are required parameters.")

        month = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        client = Client(config, log=log)
        accts = [account]
        if(all_):
            accts = client.get_slugs()
        for acct in accts:
            if(not client.get_account_by_slug(acct)):
                log.info("Skipping {}".format(acct))
                continue
            client.clear_cache_s3(acct, month)
            client.clear_cache_local(acct, month)

class ZephyrConfigure(ZephyrCLI):
    class Meta:
        label = "configure"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Gather configuration values."
        arguments = ZephyrCLI.Meta.arguments + [(
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

class ZephyrETL(ZephyrCLI):
    class Meta:
        label = "etl"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Perform Extract-Transform-Load operations on data."
        arguments = ZephyrCall.Meta.arguments

class ZephyrMeta(ZephyrCLI):
    class Meta:
        label = "meta"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Gather client meta information."
        arguments = ZephyrCLI.Meta.arguments + [(
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
        self.ZEPHYR_LINE_WIDTH = int(
            self.app.config.get("zephyr", "ZEPHYR_LINE_WIDTH")
        )
        expire_cache = self.app.pargs.expire_cache
        self.app.log.info("Collecting client metadata.")
        projects = meta.LWProjects(config, log=log)
        projects.cache_policy(expire_cache)
        self.app.render(
            projects.get_all_projects(),
            line_width=self.ZEPHYR_LINE_WIDTH
        )

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
                out = {col: row[col] for col in header}
                writer.writerow(out)


    def run(self, **kwargs):
        infile = self.app.pargs.infile
        outfile = self.app.pargs.outfile
        no_tags = self.app.pargs.no_tags
        self.app.log.info("Using input file: {infile}".format(infile=infile))
        self.app.log.info("Using output file: {outfile}".format(outfile=outfile))
        self.filter_ri_dbr(infile, outfile, no_tags)

class ZephyrData(ZephyrCall):
    class Meta:
        label = "data"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Generate single table reports for an account."
        arguments = ZephyrCall.Meta.arguments

class DataRun(ZephyrData):
    class Meta:
        stacked_on = "data"
        stacked_type = "nested"
        arguments = ZephyrData.Meta.arguments

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))


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
        self.app.log.info(
            "Using cached response: {cache}"
            .format(cache=cache_file)
        )
        if(not compute_details):
            raise NotImplementedError
        self.app.log.info(
            "Using compute_details response: {compute_details}"
            .format(compute_details=compute_details)
        )
        out = compute_av(cache_file, compute_details)
        self.app.render(out)
        return out

class ZephyrReport(ZephyrCall):
    class Meta:
        label = "report"
        stacked_on = "base"
        stacked_type = "nested"
        description = "Generate advanced reports."

class SheetRun(ZephyrReport):
    class Meta:
        stacked_on = "report"

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def alert_config_missing(self, acct, missing):
        if not self.app.pargs.all:
            raise ZephyrException(
                "Configuration missing for the following: {}."
                .format(missing)
            )
        self.app.log.info(
            "Skipped {acct}. Configuration is missing for {miss}."
            .format(acct=acct, miss=missing)
        )

    def _run(self, *sheets):
        label = self.Meta.label
        config = self.app.config
        log = self.app.log
        account = self.app.pargs.account
        all_ = self.app.pargs.all
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        if not any((account, date, expire_cache, all_)):
            self.app.args.print_help()
            sys.exit(0)
        if not any((account, all_)):
            raise ZephyrException("Account is a required parameter.")
        # If no date is given then default to the first of last month.
        if(not date):
            date = first_of_previous_month().strftime("%Y-%m-%d")
        client = Client(config, log=log)
        accts = [account]
        if all_:
            accts = client.get_slugs()
        for acct in accts:
            book = Book(
                config, label, sheets, acct, date, expire_cache, log=log
            )
            if not book.slug_valid(acct):
                missing = ", ".join({
                    validator.name
                    for validator in book.slug_validators()
                    if(not validator.get_account_by_slug(acct))
                })
                self.alert_config_missing(acct, missing)
                continue
            log.info("Running {report} for {account}".format(
                report=label,
                account=acct,
            ))
            out = book.to_xlsx()
            # Test to see if this book has any data
            sheet_set = {bool(value) for value in out.values()}
            if not any(sheet_set):
                self.app.log.info("No data to report for {}!".format(acct))
        if self.app.pargs.output_handler_override:
            ddh = book.sheets[0].ddh
            if ddh:
                self.app.render(book.sheets[0].ddh)
        return book

class AccountReview(SheetRun):
    class Meta:
        label = "account-review"
        description = "Generate an account review for a given account."

    def run(self, **kwargs):
        self._run(
            CoverPage,
            SheetBilling,
            SheetEC2,
            SheetRDS,
            SheetMigration,
            SheetRIs,
            SheetSRs,
            SheetUnderutilized,
        )

class BillingSheet(SheetRun):
    class Meta:
        label = "billing"
        description = "Generate the compute-details worksheet."

    def run(self, **kwargs):
        self._run(SheetBilling)

class ComputeDetailsSheet(SheetRun):
    class Meta:
        label = "compute-details"
        description = "Generate the compute-details worksheet."

    def run(self, **kwargs):
        self._run(SheetEC2)

class ComputeMigrationSheet(SheetRun):
    class Meta:
        label = "compute-migration"
        description = "Generate the compute-migration worksheet."

    def run(self, **kwargs):
        self._run(SheetMigration)

class ComputeRISheet(SheetRun):
    class Meta:
        label = "compute-ri"
        description = "Generate the compute-ri worksheet."

    def run(self, **kwargs):
        self._run(SheetRIs)

class DBDetailsSheet(SheetRun):
    class Meta:
        label = "db-details"
        description = "Generate the db-details worksheet."

    def run(self, **kwargs):
        self._run(SheetRDS)

class DBIdleSheet(SheetRun):
    class Meta:
        label = "db-idle"
        description = "Generate the db-idle worksheet."

    def run(self, **kwargs):
        self._run(SheetDBIdle)

class IAMUsersSheet(SheetRun):
    class Meta:
        label = "iam-users"
        description = "Generate the iam-users worksheet."

    def run(self, **kwargs):
        self._run(SheetIAMUsers)

class LBIdleSheet(SheetRun):
    class Meta:
        label = "lb-idle"
        description = "Generate the db-idle worksheet."

    def run(self, **kwargs):
        self._run(SheetLBIdle)

class ServiceRequestSheet(SheetRun):
    class Meta:
        label = "service-requests"
        description = "Generate the service-requests worksheet."

    def run(self, **kwargs):
        self._run(SheetSRs)

class StorageDetachedSheet(SheetRun):
    class Meta:
        label = "storage-detached"
        description = "List detached storage volumes."

    def run(self, **kwargs):
        self._run(SheetStorageDetached)


__ALL__ = [
    AccountReview,
    BillingSheet,
    ComputeAV,
    ComputeDetailsSheet,
    ComputeMigrationSheet,
    ComputeRISheet,
    DBDetailsSheet,
    DBIdleSheet,
    IAMUsersSheet,
    LBIdleSheet,
    StorageDetachedSheet,
    Domains,
    ServiceRequestSheet,
    ZephyrCLI,
    ZephyrClearCache,
    ZephyrConfigure,
    ZephyrDBRRI,
    ZephyrData,
    ZephyrETL,
    ZephyrMeta,
    ZephyrReport,
]
