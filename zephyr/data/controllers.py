import csv
import io
import os

from datetime import datetime

from botocore.exceptions import ClientError
from cement.core.controller import CementBaseController, expose

from ..core import cloudcheckr
from ..core.aws import get_session, upload_file
from ..core.ddh import DDH
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
            ["--account"], dict(
                 type=str,
                 help="The desired account short name."
            )
        ),
        (
            ["--cache"], dict(
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

class WarpRun(DataRun):
    def cache_policy(self, WarpClass, account, date, cache_override, expired):
        log = self.app.log.info
        api_key = self.app.config.get("cloudcheckr", "api_key")
        base = self.app.config.get("cloudcheckr", "base")
        bucket = self.app.config.get("lw-aws", "s3_bucket")
        key_id = self.app.config.get("lw-aws", "AWS_ACCESS_KEY_ID")
        secret = self.app.config.get("lw-aws", "AWS_SECRET_ACCESS_KEY")
        accounts = os.path.expanduser(self.app.config.get("zephyr", "accounts"))
        cache_root = os.path.expanduser(self.app.config.get("zephyr", "cache"))

        if(account):
            cc_name = cloudcheckr.get_cloudcheckr_name(account, accounts)

        cache_file = False
        if(date):
            month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
            cache_dir = os.path.join(account, month)
            folder = os.path.join(cache_root, cache_dir)
            cache_file = cloudcheckr.cache_path(folder, WarpClass.slug)

        cache_local = cache_file and os.path.isfile(cache_file)
        if(cache_override):
            cache = cache_override
        elif(cache_local):
            cache = cache_file

        fresh = cache_local and not expired
        if(cache_override or fresh):
            log("Using cached response: {cache}".format(cache=cache))
            with open(cache, "r") as f:
                return f.read()
        session = get_session(key_id, secret)
        s3_key = cloudcheckr.cache_path(cache_dir, WarpClass.slug)
        s3 = session.resource("s3")
        cache_s3 = False
        cache_temp = io.BytesIO()
        try:
            s3.meta.client.download_fileobj(
                bucket,
                s3_key,
                cache_temp
            )
        except ClientError as e:
            pass
        cache_s3 = cache_temp.getvalue()
        if(cache_s3 and not expired):
            with open(cache_file, "wb") as cache_fd:
                log("Using cached response from S3.")
                cache_fd.write(cache_s3)
                return cache_s3.decode("utf-8")
        cached = (cache_s3 or cache_local)
        if(expired or not cached):
            log("Retrieving data from CloudCheckr.")
            return cloudcheckr.cache(
                WarpClass,
                base,
                api_key,
                cc_name,
                date,
                cache_root=cache_root,
                cache_dir=cache_dir,
                bucket=bucket,
                session=session,
                log=log,
            )

    def warp_run(self, WarpClass, **kwargs):
        account = self.app.pargs.account
        cache_arg = self.app.pargs.cache
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        cache = None
        if(cache_arg):
            cache = os.path.expanduser(cache_arg)
        response = self.cache_policy(WarpClass, account, date, cache, expire_cache)
        warp = WarpClass(response)
        self.app.render(warp.to_ddh())

class Billing(DataRun):
    def cache_policy(self, cache):
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
            data = [[row[col] for col in header] for row in reader]
        return DDH(header=header, data=data)

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        out = self.cache_policy(cache)
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
