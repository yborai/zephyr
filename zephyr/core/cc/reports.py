
from ...report.ec2 import ec2_sheet
from ...report.migration import migration_sheet
from ...report.rds import rds_sheet
from ...report.ri_recs import ri_sheet
from ..report import Report
from .calls import (
    ComputeDetailsWarp,
    ComputeMigrationWarp,
    ComputeRIWarp,
    DBDetailsWarp,
)

class ReportEC2(Report):
    name = "EC2s"
    title = "EC2 Details"
    cls = ComputeDetailsWarp

    @staticmethod
    def _xlsx(*args, **kwargs):
        return ec2_sheet(*args, **kwargs)

class ReportMigration(Report):
    name = "Migration"
    title = "EC2 Migration Recommendations"
    cls = ComputeMigrationWarp

    @staticmethod
    def _xlsx(*args, **kwargs):
        return migration_sheet(*args, **kwargs)

class ReportRDS(Report):
    name = "RDS"
    title = "RDS Details"
    cls = DBDetailsWarp

    @staticmethod
    def _xlsx(*args, **kwargs):
        return rds_sheet(*args, **kwargs)

class ReportRIs(Report):
    name = "RIs"
    title = "EC2 RI Recommendations"
    cls = ComputeRIWarp

    @staticmethod
    def _xlsx(*args, **kwargs):
        return ri_sheet(*args, **kwargs)
