from cement.core import handler, controller

from .ec2_details import ToolkitInstanceDetails

from .rds_details import ToolkitRdsDetails

from .ec2_migration_recommendations import ToolkitEC2MigrationRecommendations

from .ec2_ri_recommendations import ToolkitEC2RIRecommendations

from .ec2_underutilized_instances import ToolkitEC2UnderutilizedInstances

from .service_requests import ToolkitServiceRequests

from .ec2_underutilized_instances_breakdown import ToolkitEC2UnderutilizedInstancesBreakdown

from .ri_pricings import ToolkitRiPricings

def load(app):
    handler.register(ToolkitRiPricings)
    handler.register(ToolkitEC2UnderutilizedInstancesBreakdown)
    handler.register(ToolkitServiceRequests)
    handler.register(ToolkitEC2UnderutilizedInstances)
    handler.register(ToolkitEC2MigrationRecommendations)
    handler.register(ToolkitEC2RIRecommendations)
    handler.register(ToolkitRdsDetails)
    handler.register(ToolkitInstanceDetails)
    handler.register(ToolkitDataController)

class ToolkitDataController(controller.CementBaseController):
    class Meta:
        label = 'data'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Generate single table reports for an account."
    
    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()
