import os

from cement.core.foundation import CementApp
from cement.core.exc import FrameworkError
from cement.utils import fs, misc
from cement.utils.misc import init_defaults

from .cli.controllers import (
    ZephyrCLI,
        ZephyrData,
        ZephyrReport,
            ZephyrAccountReview,
        ZephyrETL,
)

from .data.billing_line_item_aggregates import ZephyrBillingLineItemAggregates
from .data.billing_line_items import ZephyrBillingLineItems
from .data.billing_monthly import ZephyrBillingMonthly
from .data.compute_av import ZephyrComputeAV 
from .data.compute_details import ZephyrComputeDetails
from .data.compute_migration import ZephyrComputeMigration
from .data.compute_ri import ZephyrComputeRI
from .data.compute_underutilized import ZephyrComputeUnderutilized
from .data.compute_underutilized_breakdown import ZephyrComputeUnderutilizedBreakdown
from .data.db_details import ZephyrDBDetails
from .data.db_idle import ZephyrDBIdle
from .data.lb_idle import ZephyrLBIdle
from .data.ri_pricings import ZephyrRIPricings
from .data.service_requests import ZephyrServiceRequests
from .data.storage_detached import ZephyrStorageDetached
from .data.iam_users import ZephyrIAMUsers
from .etl.dbr_ri import ZephyrDBRRI


defaults = init_defaults("zephyr", "log.logging")
defaults["log.logging"]["level"] = os.environ.get("ZEPHYR_DEBUG_LEVEL", "INFO")
defaults["log.colorlog"] = defaults["log.logging"]
defaults["zephyr"]["data_dir"] = "~/.zephyr"

class Zephyr(CementApp):
    class Meta:
        label = "zephyr"
        base_controller = "base"
        config_defaults = defaults
        handlers = [
            ZephyrCLI,
                ZephyrData,
                    ZephyrBillingLineItemAggregates,
                    ZephyrBillingLineItems,
                    ZephyrBillingMonthly,
                    ZephyrComputeAV,
                    ZephyrComputeDetails,
                    ZephyrComputeMigration,
                    ZephyrComputeRI,
                    ZephyrComputeUnderutilized,
                    ZephyrComputeUnderutilizedBreakdown,
                    ZephyrDBDetails,
                    ZephyrDBIdle,
                    ZephyrLBIdle,
                    ZephyrRIPricings,
                    ZephyrServiceRequests,
                    ZephyrStorageDetached,
                    ZephyrIAMUsers,
                ZephyrETL,
                    ZephyrDBRRI,
                ZephyrReport,
                    ZephyrAccountReview,
        ]
        extensions = [
            "zephyr.cli.output",
            "colorlog",
            "mustache",
        ]
        output_handler = "mustache"
        log_handler = "colorlog"

def main():
    with Zephyr() as app:
        try:
            app.run()
        except FrameworkError as e:
            if not getattr(app.pargs, "output_handler_override", True):
                app.log.error("No output handler specified. Set with the -o flag.")
            raise e

if __name__ == "__main__":
    main()
