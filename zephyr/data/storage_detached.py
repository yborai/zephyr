from .core import BestPracticesWarp

def create_sheet(json_string, csv_filename="storage-detached.csv"):
    processor = StorageDetachedWarp(json_string)
    return processor.write_csv(csv_filename)

class StorageDetachedWarp(BestPracticesWarp):
    bpc_id = 1
    slug = "storage-detached"

    def _fieldnames(self):
        return (
            "Volume ID",
            "Size",
            "Predicted Monthly Cost",
            "EC2 Instance",
            "Region",
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )
