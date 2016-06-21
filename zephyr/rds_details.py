from .core import Sheet


def create_sheet(json_string, csv_filename='rds_details.csv'):
    processor = RDSDetailsSheet(json_string)
    return processor.write_csv(csv_filename)


class RDSDetailsSheet(Sheet):
    def _data_key(self):
        return 'RdsDbInstances'

    def _filter_row(self, details_row):
        return {
            key: details_row[key] for key in self._fieldnames() if key in details_row.keys()
        }

    def _fieldnames(self):
        return (
            'DbInstanceId', 'DbInstanceName', 'MonthlyCost', 'RegionName',
            'DbInstanceClass', 'Engine', 'EngineVersion', 'LicenseModel',
            'AllocatedStorageGB', 'FreeStorageSpaceBytes', 'Endpoint',
            'BackupRetentionPeriod'
        )
