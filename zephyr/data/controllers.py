import csv

from cement.core.controller import CementBaseController, expose

from .common import DDH
from .compute_av import compute_av
from .compute_details import ComputeDetailsWarp
from .compute_migration import ComputeMigrationWarp
from .compute_ri import ComputeRIWarp
from .compute_underutilized import ComputeUnderutilizedWarp
from .compute_underutilized_breakdown import ComputeUnderutilizedBreakdownWarp
from .db_details import DBDetailsWarp
from .db_idle import DBIdleWarp
from .domains import domains
from .iam_users import iam_users
from .lb_idle import LBIdleWarp
from .ri_pricings import RIPricingWarp
from .service_requests import ServiceRequestWarp
from .storage_detached import StorageDetachedWarp

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
        ), ]

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

class WarpRun(DataRun):
    def warp_run(self, WarpClass, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = WarpClass(response)
        self.app.render(warp.to_ddh())

class Billing(DataRun):
    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
            data = [[row[col] for col in header] for row in reader]
        out = DDH(header=header, data=data)
        self.app.render(out)
        return out

class BillingMonthly(Billing):
    class Meta:
        label = "billing-monthly"
        description = "Get the monthly billing meta information."

class BillingLineItems(Billing):
    class Meta:
        label = "billing-line-items"
        description = "Get the line items billing meta information."

class BillingLineItemAggregates(Billing):
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
        cache = self.app.pargs.cache
        compute_details = self.app.pargs.compute_details
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        if(not compute_details):
            raise NotImplementedError
        self.app.log.info("Using compute_details response: {compute_details}".format(compute_details=compute_details))
        out = compute_av(cache, compute_details)
        self.app.render(out)
        return out

class ComputeDetails(WarpRun):
    class Meta:
        label = "compute-details"
        description = "Get the detailed instance meta information."

    def run(self, **kwargs):
        self.warp_run(ComputeDetailsWarp, **kwargs)

class ComputeMigration(WarpRun):
    class Meta:
        label = "compute-migration"
        description = "Get the migration recommendations meta information"

    def run(self, **kwargs):
        self.warp_run(ComputeMigrationWarp, **kwargs)

class ComputeRI(WarpRun):
    class Meta:
        label = "compute-ri"
        description = "Get the ri recommendations meta information."

    def run(self, **kwargs):
        self.warp_run(ComputeRIWarp, **kwargs)

class ComputeUnderutilized(WarpRun):
    class Meta:
        label = "compute-underutilized"
        description = "Get the underutilized instance meta information"

    def run(self, **kwargs):
        self.warp_run(ComputeUnderutilizedWarp, **kwargs)

class ComputeUnderutilizedBreakdown(WarpRun):
    class Meta:
        label = "compute-underutilized-breakdown"
        description = "Get the underutilized instance breakdown meta information"

    def run(self, **kwargs):
        self.warp_run(ComputeUnderutilizedBreakdownWarp, **kwargs)

class DBDetails(WarpRun):
    class Meta:
        label = "db-details"
        description = "Get the detailed rds meta information"

    def run(self, **kwargs):
        self.warp_run(DBDetailsWarp, **kwargs)

class DBIdle(WarpRun):
    class Meta:
        label = "db-idle"
        description = "List idle database instances."

    def run(self, **kwargs):
        self.warp_run(DBIdleWarp, **kwargs)

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
        cache = self.app.pargs.cache
        if (not cache):
            raise NotImplementedError # We will add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        out = iam_users(cache)
        self.app.render(out)
        return out

class LBIdle(WarpRun):
    class Meta:
        label = "lb-idle"
        description = "List idle load balancers."

    def run(self, **kwargs):
        self.warp_run(LBIdleWarp, **kwargs)

class RIPricings(WarpRun):
    class Meta:
        label = "ri-pricings"
        description = "Get the detailed ri pricings meta information."

    def run(self, **kwargs):
        self.warp_run(RIPricingWarp, **kwargs)

class ServiceRequests(WarpRun):
    class Meta:
        label = "service-requests"
        description = "get the detailed service requests meta information."

    def run(self, **kwargs):
        self.warp_run(ServiceRequestWarp, **kwargs)

class StorageDetached(WarpRun):
    class Meta:
        label = "storage-detached"
        description = "List detached storage volumes."

    def run(self, **kwargs):
        self.warp_run(StorageDetachedWarp, **kwargs)

__ALL__ = [
    ZephyrData,
    BillingMonthly,
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
    ServiceRequests,
    StorageDetached,
]
