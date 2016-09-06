from cement.core import handler, controller

from .common import ToolkitDataController
from .billing_monthly import ToolkitBillingMonthly
from .compute_details import ToolkitComputeDetails
from .compute_migration import ToolkitComputeMigration
from .compute_ri import ToolkitComputeRI
from .compute_underutilized import ToolkitComputeUnderutilized
from .compute_underutilized_breakdown import ToolkitComputeUnderutilizedBreakdown
from .db_details import ToolkitDBDetails
from .db_idle import ToolkitDBIdle
from .lb_idle import ToolkitLBIdle
from .ri_pricings import ToolkitRiPricings
from .service_requests import ToolkitServiceRequests
from .storage_detached import ToolkitStorageDetached
from .compute_av import ToolkitComputeAV
from .iam_users import ToolkitIamUsers

def load(app):
    handler.register(ToolkitDataController)

    handler.register(ToolkitBillingMonthly)
    handler.register(ToolkitComputeDetails)
    handler.register(ToolkitComputeMigration)
    handler.register(ToolkitComputeRI)
    handler.register(ToolkitComputeUnderutilized)
    handler.register(ToolkitComputeUnderutilizedBreakdown)
    handler.register(ToolkitDBDetails)
    handler.register(ToolkitDBIdle)
    handler.register(ToolkitLBIdle)
    handler.register(ToolkitRiPricings)
    handler.register(ToolkitServiceRequests)
    handler.register(ToolkitStorageDetached)
    handler.register(ToolkitComputeAV)
    handler.register(ToolkitIamUsers)