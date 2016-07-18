from cement.core import handler, controller

from .common import ToolkitDataController
from .billing_monthly import ToolkitBillingMonthly
from .ec2_details import ToolkitInstanceDetails
from .rds_details import ToolkitRdsDetails
from .ec2_migration_recommendations import ToolkitEC2MigrationRecommendations
from .ec2_ri_recommendations import ToolkitEC2RIRecommendations
from .ec2_underutilized_instances import ToolkitEC2UnderutilizedInstances
from .service_requests import ToolkitServiceRequests
from .ec2_underutilized_instances_breakdown import ToolkitEC2UnderutilizedInstancesBreakdown
from .ri_pricings import ToolkitRiPricings

def load(app):
    handler.register(ToolkitDataController)

    handler.register(ToolkitBillingMonthly)
    handler.register(ToolkitEC2MigrationRecommendations)
    handler.register(ToolkitEC2RIRecommendations)
    handler.register(ToolkitEC2UnderutilizedInstances)
    handler.register(ToolkitEC2UnderutilizedInstancesBreakdown)
    handler.register(ToolkitInstanceDetails)
    handler.register(ToolkitRdsDetails)
    handler.register(ToolkitRiPricings)
    handler.register(ToolkitServiceRequests)
