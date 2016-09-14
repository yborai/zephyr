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
    @expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

class Billing(DataRun):
    class Meta:
        stacked_on = "data"
        stacked_type = "nested"

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
        stacked_on = "data"
        stacked_type = "nested"
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

class ComputeDetails(DataRun):
    class Meta:
        label = "compute-details"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the detailed instance meta information."

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = ComputeDetailsWarp(response)
        self.app.render(warp.to_ddh())

class ComputeMigration(DataRun):
    class Meta:
        label = "compute-migration"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the migration recommendations meta information"

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = ComputeMigrationWarp(response)
        self.app.render(warp.to_ddh())

class ComputeRI(DataRun):
    class Meta:
        label = "compute-ri"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the ri recommendations meta information."

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = ComputeRIWarp(response)
        self.app.render(warp.to_ddh())

class ComputeUnderutilized(DataRun):
    class Meta:
        label = "compute-underutilized"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the underutilized instance meta information"

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We'll add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = ComputeUnderutilizedWarp(response)
        self.app.render(warp.to_ddh())

class ComputeUnderutilizedBreakdown(DataRun):
    class Meta:
        label = "compute-underutilized-breakdown"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the underutilized instance breakdown meta information"

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We'll add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = ComputeUnderutilizedBreakdownWarp(response)
        self.app.render(warp.to_ddh())

class DBDetails(DataRun):
    class Meta:
        label = "db-details"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the detailed rds meta information"

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError #We will add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = DBDetailsWarp(response)
        self.app.render(warp.to_ddh())

class DBIdle(DataRun):
    class Meta:
        label = "db-idle"
        stacked_on = "data"
        stacked_type = "nested"
        description = "List idle database instances."

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = DBIdleWarp(response)
        self.app.render(warp.to_ddh())

class IAMUsers(DataRun):
    class Meta:
        label = "iam-users"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the IAM Users meta information"

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if (not cache):
            raise NotImplementedError # We will add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        out = iam_users(cache)
        self.app.render(out)
        return out

class LBIdle(DataRun):
    class Meta:
        label = "lb-idle"
        stacked_on = "data"
        stacked_type = "nested"
        description = "List idle load balancers."

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = LBIdleWarp(response)
        self.app.render(warp.to_ddh())

class RIPricings(DataRun):
    class Meta:
        label = "ri-pricings"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the detailed ri pricings meta information."

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = RIPricingWarp(response)
        self.app.render(warp.to_ddh())

class ServiceRequests(DataRun):
    class Meta:
        label = "service-requests"
        stacked_on = "data"
        stacked_type = "nested"
        description = "get the detailed service requests meta information."

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # we will add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache,"r") as f:
            response = f.read()
        warp = ServiceRequestWarp(response)
        self.app.render(warp.to_ddh())

class StorageDetached(DataRun):
    class Meta:
        label = "storage-detached"
        stacked_on = "data"
        stacked_type = "nested"
        description = "List detached storage volumes."

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = StorageDetachedWarp(response)
        self.app.render(warp.to_ddh())

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
    IAMUsers,
    LBIdle,
    RIPricings,
    ServiceRequests,
    StorageDetached,
]
