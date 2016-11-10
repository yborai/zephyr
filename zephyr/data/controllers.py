import csv
import io
import sqlite3
import os

from datetime import datetime

from cement.core.controller import CementBaseController, expose

from ..cli.controllers import ZephyrCLI
from ..core import aws, cloudcheckr as cc, lo
from ..core.ddh import DDH
from .common import get_config_values
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
from .service_requests import ServiceRequests
from .storage_detached import StorageDetachedWarp

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

class WarpRun(DataRun):
    def cache_key(account, date):
        month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        filename = "{slug}.json".format(date=date, slug=self.slug)
        return os.path.join(account, month, filename)

    def cache(self, WarpClass, account, date, cache_file, expired):
        config = self.app.config
        log = self.app.log
        # If cache_file is specified then use that
        if(cache_file):
            log.info("Using specified cached response: {cache}".format(cache=cache_file))
            with open(cache_file, "r") as f:
                return f.read()
        zephyr_config_keys = ("cache", "database")
        cache_root, db = [
            os.path.expanduser(path)
            for path in get_config_values("zephyr", zephyr_config_keys, config)
        ]
        database = sqlite3.connect(os.path.join(cache_root, db))
        cc_config_keys = ("api_key", "base")
        api_key, base = get_config_values("cloudcheckr", cc_config_keys, config)
        # If no date is given then default to the first of last month.
        now = datetime.now()
        if(not date):
            date = datetime(year=now.year, month=now.month-1, day=1).strftime("%Y-%m-%d")
        month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        cache_dir = os.path.join(account, month)
        folder = os.path.join(cache_root, cache_dir)

        # If local exists and expired is false then use the local cache
        cache_key = self.cache_key(account, date)
        cache_local = os.path.join(cache_root, cache_key)
        #
        cache_local_exists = os.path.isfile(cache_local)
        if(cache_local_exists and not expired):
            log.info("Using cached response: {cache}".format(cache=cache_local))
            with open(cache_local, "r") as f:
                return f.read()
        # If local does not exist and expired is false then check s3
        aws_config_keys = ("s3_bucket", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")
        bucket, key_id, secret = get_config_values("lw-aws", aws_config_keys, config)
        session = aws.get_session(key_id, secret)
        s3 = session.resource("s3")
        cache_s3 = aws.get_object_from_s3(bucket, cache_key, s3)
        if(cache_s3 and not expired):
            log.info("Using cached response from S3.")
            with open(cache_local, "wb") as cache_fd:
                cache_fd.write(cache_s3)
            return cache_s3.decode("utf-8")
        # If we are this far then contact the API and cache the result
        cc_name = cc.get_account_by_slug(account, database)
        log.info("Retrieving data from CloudCheckr.")
        return cc.cache(
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
        cache_file = self.app.pargs.cache_file
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        cache_file_ = None
        if(cache_file):
            cache_file_ = os.path.expanduser(cache_file)
        response = self.cache(WarpClass, account, date, cache_file_, expire_cache)
        warp = WarpClass(response)
        self.app.render(warp.to_ddh())

class Billing(DataRun):
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

class ServiceRequestsRun(DataRun):
    class Meta:
        label = "service-requests"
        description = "get the detailed service requests meta information."

    def run(self, **kwargs):
        account = self.app.pargs.account
        cache_file = self.app.pargs.cache_file
        date = self.app.pargs.date
        expire_cache = self.app.pargs.expire_cache
        response = ServiceRequests.cache(
            account, date, cache_file, expire_cache, config=self.app.config, log=self.app.log
        )
        out = ServiceRequests(response)
        self.app.render(out.to_ddh())
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
        cache_file = self.app.pargs.cache_file
        if (not cache_file):
            raise NotImplementedError # We will add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache_file))
        out = iam_users(cache_file)
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
    ServiceRequestsRun,
    StorageDetached,
]
