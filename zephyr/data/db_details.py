from .core import Warp

def create_sheet(json_string, csv_filename="db-details.csv"):
    processor = DBDetailsWarp(json_string)
    return processor.write_csv(csv_filename)

class DBDetailsWarp(Warp):
    slug = "db-details"
    uri = "inventory.json/get_resources_rds_details"

    def _key(self):
        return "RdsDbInstances"

    def _filter_row(self, details_row):
        return {
            key: details_row[key] for key in self._fieldnames() if key in details_row.keys()
        }

    def _fieldnames(self):
        return (
            "DbInstanceId", "DbInstanceName", "MonthlyCost", "RegionName",
            "DbInstanceClass", "Engine", "EngineVersion", "LicenseModel",
            "AllocatedStorageGB", "FreeStorageSpaceBytes", "Endpoint",
            "BackupRetentionPeriod"
        )
