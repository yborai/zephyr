import csv
import os

from datetime import datetime

from cement.core.controller import CementBaseController, expose

from ..cli.controllers import ZephyrCLI
from ..core.ddh import DDH
from ..core.utils import ZephyrException
from ..core.bd.calls import compute_av
from ..core.boto.calls import domains
from ..core.cc.calls import (
    BestPracticeChecksSummary,
    ComputeDetailsWarp,
    ComputeMigrationWarp,
    ComputeRIWarp,
    ComputeUnderutilizedWarp,
    ComputeUnderutilizedBreakdownWarp,
    DBDetailsWarp,
    DBIdleWarp,
    IAMUsersData,
    LBIdleWarp,
    RIPricingWarp,
    StorageDetachedWarp,
)
from ..core.dy.calls import Billing
from ..core.lo.calls import ServiceRequests

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
            ["--cache-file"], dict(
                 type=str,
                 help="The path to the cached response to use."
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

class DataRun(ZephyrData):
    class Meta:
        stacked_on = "data"
        stacked_type = "nested"
        arguments = ZephyrData.Meta.arguments

    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run_call(self, cls, **kwargs):
        account = self.app.pargs.account
        cache_file = self.app.pargs.cache_file
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        log = self.app.log
        cache_file_ = None
        if(cache_file):
            cache_file_ = os.path.expanduser(cache_file)
        client = cls(config=self.app.config)
        accts = [account]
        if(account == "all"):
            accts = client.get_slugs()
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
                    cache_file_,
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

    def run(self, **kwargs):
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
        description = "Get the underutilized instance meta information"

    def run(self, **kwargs):
        self.run_call(ComputeUnderutilizedWarp, **kwargs)

class ComputeUnderutilizedBreakdown(DataRun):
    class Meta:
        label = "compute-underutilized-breakdown"
        description = "Get the underutilized instance breakdown meta information"

    def run(self, **kwargs):
        self.run_call(ComputeUnderutilizedBreakdownWarp, **kwargs)

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

class BillingRun(DataRun):
    def cache(self, cache_file):
        if(not cache_file):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache_file))
        with open(cache_file, "r") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
            data = [[row[col] for col in header] for row in reader]
        return DDH(header=header, data=data)

    def run(self, **kwargs):
        cache_file = self.app.pargs.cache_file
        out = self.cache(cache_file)
        self.app.render(out)
        return out

class BillingLineItemAggregates(BillingRun):
    class Meta:
        label = "billing-line-item-aggregates"
        description = "Get the billing line item aggregate totals."

class ComputeAV(DataRun):
    class Meta:
        label = "compute-av"
        description = "Get the AV of instance meta information"

        arguments = DataRun.Meta.arguments + [(
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

__ALL__ = [
    ZephyrData,
    BestPracticeChecksSummaryData,
    BillingLineItems,
    BillingLineItemAggregates,
    ComputeAV,
    ComputeDetails,
    ComputeMigration,
    ComputeRI,
    ComputeUnderutilized,
    ComputeUnderutilizedBreakdown,
    DBDetails,
    DBIdle,
    Domains,
    IAMUsers,
    LBIdle,
    RIPricings,
    ServiceRequestsRun,
    StorageDetached,
]
