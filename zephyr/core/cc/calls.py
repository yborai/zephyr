import csv
import json

from datetime import datetime
from itertools import groupby

from ..ddh import DDH
from ..utils import ZephyrException, timed
from . import client as cc
from .core import BestPracticesWarp, SplitInstanceWarp, Warp

class CloudCheckrAccounts(cc.CloudCheckr):
    uri = "account.json/get_accounts_v2"
    def __init__(self, config, log=None):
        super().__init__(config)
        self.log = log

    def request(self):
        params = dict(access_key=self.api_key)
        url = "".join([
            self.base,
            self.uri,
            "?",
            urlencode(params),
        ])
        r = timed(lambda:requests.get(url), log=self.log.info)()
        accts = r.json()
        header = ["aws_account", "id", "name"]
        data = [[
                acct["aws_account_id"],
                acct["cc_account_id"],
                acct["account_name"],
            ]
            for acct in accts["accounts_and_users"]
        ]
        df = pd.DataFrame(data, columns=header)
        df.to_sql("cloudcheckr_accounts", self.database, if_exists="replace")

class ComputeDetailsWarp(Warp):
    slug = "compute-details"
    uri = "inventory.json/get_resources_ec2_details"

    def _key(self):
        return "Ec2Instances"

    def _filter_row(self, details_row):
        filtered_row = {
            key: details_row[key] for key in self._fieldnames() if key in details_row.keys()
        }

        return self._format_datefields(filtered_row)

    def _format_datefields(self, row):
        for field in self._datetime_fields():
            if(row[field] is None):
                continue
            row[field] = datetime.strptime(
                row[field], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%m/%d/%y %H:%M")

        return row

    def _fieldnames(self):
        return (
            "InstanceId",
            "InstanceName",
            "PrivateIpAddress",
            "Status",
            "Region",
            "PricingPlatform",
            "InstanceType",
            "LaunchTime"
        )

    def _datetime_fields(self):
        return ("LaunchTime",)

class ComputeMigrationWarp(SplitInstanceWarp):
    bpc_id = 240
    slug = "compute-migration"

    def _fieldnames(self):
        return (
            "Instance ID", "Instance Name", "Region", "Recommendation",
            "On-Demand Current Monthly Cost", "Cost for Recommended",
            "Yearly Savings", "Platform", "vCPU for current",
            "vCPU for next gen", "Memory for current", "Memory for next gen"
        )

    def _money_fields(self):
        return (
            "On-Demand Current Monthly Cost", "Cost for Recommended", "Yearly Savings"
        )

class ComputeRIWarp(BestPracticesWarp):
    bpc_id = 190
    slug = "compute-ri"

    def _fieldnames(self):
        return (
            "Number", "Instance Type", "AZ", "Platform", "Commitment Type",
            "Tenancy", "Upfront RI Cost", "Reserved Monthly Cost",
            "On-Demand Monthly Cost", "Total Savings"
        )

    def _money_fields(self):
        return (
            "Upfront RI Cost", "Reserved Monthly Cost",
            "On-Demand Monthly Cost", "Total Savings"
        )

class ComputeUnderutilizedWarp(SplitInstanceWarp):
    bpc_id = 68
    slug = "compute-underutilized"

    def _fieldnames(self):
        return (
            "Instance ID", "Instance Name", "Average CPU Util",
            "Predicted Monthly Cost", "Region"
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )

class ComputeUnderutilizedBreakdownWarp(SplitInstanceWarp):
    @classmethod
    def create_sheet(cls, json_string, define_category_func, csv_filename='compute-underutilized-breakdown.csv'):
        """
        This function creates new class instance
        with provided define_category function
        and immediately writes the parsed json review
        to specified csv file.

        define_category_func should take one string argument
        and returns string which contains category name.
        """
        processor = cls(json_string, define_category_func)
        return processor.write_csv(csv_filename)

    def __init__(self, json_string, define_category_func):
        self.define_category_func = define_category_func
        super().__init__(json_string, bpc_id=68)

    def write_csv(self, csv_filename):
        filtered_rows = (
            self._filter_row(details_row)
            for details_row in self.data[self._key()]
        )

        grouped_rows = self._group_rows(filtered_rows)
        self._write_to_file(csv_filename, grouped_rows)

        return csv_filename

    def _write_to_file(self, csv_filename, grouped_rows):
        with open(csv_filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self._fieldnames())

            writer.writeheader()
            for category, group in grouped_rows:
                category_sum = 0
                for row in group:
                    category_sum += row["Predicted Monthly Cost"]
                    writer.writerow(row)
                writer.writerow({
                    "Category": row["Category"],
                    "Predicted Monthly Cost": category_sum,
                })
                writer.writerow(self._empty_row())
        return csv_filename

    def _filter_row(self, details_row):
        details_row["Instance ID"] = self._get_instance_id(details_row[self._instance_field()])
        details_row["Instance Name"] = self._get_instance_name(details_row[self._instance_field()])
        details_row["Category"] = self._define_category(details_row["Instance Name"].split("-")[0])

        return super()._filter_row(details_row)

    def _group_rows(self, filtered_rows):
        rows = sorted(filtered_rows, key=lambda row: row['Category'], reverse=True)
        return groupby(rows, lambda row: row['Category'])

    def _define_category(self, raw_category):
        """
        This method tries to call define_category function
        for current class instance and returns the result of computing
        or raises an exception if define_category_func isn't callable.
        """
        if callable(self.define_category_func):
            return self.define_category_func(raw_category)

        raise ZephyrException("define_category_func parameter should be callable")

    def _fieldnames(self):
        return (
            "Category", "Instance ID", "Instance Name", "Average CPU Util",
            "Predicted Monthly Cost", "Region"
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )

    def _empty_row(self):
        return {}

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

class DBIdleWarp(BestPracticesWarp):
    bpc_id = 134
    slug = "db-idle"

    def _fieldnames(self):
        return (
            "DB Instance",
            "Average Read IOPS",
            "Average Write IOPS",
            "Predicted Monthly Cost",
            "Region",
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )

class IAMUsersData(cc.CloudCheckr):
    slug = "iam-users"
    uri = "inventory.json/get_resources_iam_users"

    def __init__(self, json_string=None, config=None):
        if(config):
            super().__init__(config)
        if(json_string):
            self.parse(json_string)

    def parse(self, json_string):
        self.raw_json = json.loads(json_string)

        self.user_details = self.raw_json[0].get("IamUsersDetails")

        self.header = [
            "Username",
            "Has MFA",
            "Console Last Used",
            "Access Key 1 Last Used",
            "Access Key 2 Last Used",
        ]


        self.data = [
            [
                user["UserName"],
                user["HasMfa"],
                user["LastUsed"],
                user["UserCredential"]["AccessKey1LastUsedDate"],
                user["UserCredential"]["AccessKey2LastUsedDate"],
            ]
                for user in self.user_details
        ]

    def to_ddh(self):
        header = self.header
        data = self.data

        return DDH(header=header, data=data)

class LBIdleWarp(BestPracticesWarp):
    bpc_id = 126
    slug = "lb-idle"

    def _fieldnames(self):
        return (
            "Load Balancer",
            "Average Hourly Request Count",
            "Predicted Monthly Cost",
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )

class RIPricingWarp(BestPracticesWarp):
    def __init__(self, csv_filepath):
        self._read_from_csv(csv_filepath)

        grouped_csv_data = self._prepare_csv_total_data()
        self.data = {self._key(): grouped_csv_data}

    def _filter_row(self, details_row):
        filtered_row = {
            key: details_row[key]
            for key in self._fieldnames() if key in details_row.keys()
        }

        return filtered_row

    def _read_from_csv(self, csv_filepath):
        with open(csv_filepath) as csvfile:
            self.csv_data = list(csv.DictReader(list(csvfile)[5:]))

    def _prepare_csv_total_data(self):
        csv_data = sorted(self.csv_data, key=self._csv_group_keys, reverse=True)
        csv_data = groupby(csv_data, self._csv_group_keys)

        grouped_csv_data = []
        for group, data in csv_data:
            total_data = {}
            for row in data:
                if self._is_second_date(total_data, row):
                    break

                total_data['Region'] = row['Location']
                total_data['EffectiveDate'] = row['EffectiveDate']
                total_data['Instance Type'] = row['Instance Type']
                total_data['Tenancy'] = row['Tenancy']
                total_data['Platform'] = row['Operating System']
                total_data['Payment Type'] = row['PurchaseOption']
                total_data['Term'] = 12 if row['LeaseContractLength'] == '1yr' else 36

                if row['Unit'] == 'Quantity':
                    total_data['Upfront'] = row['PricePerUnit']
                else:
                    total_data['Monthly'] = row['PricePerUnit']

            if total_data['Payment Type'] == 'All Upfront':
                total_data['Monthly'] = 0
            if total_data['Payment Type'] == 'No Upfront':
                total_data['Upfront'] = 0

            if total_data['Payment Type'] and total_data['Region']:
                grouped_csv_data.append(total_data)

        return grouped_csv_data

    def _is_second_date(self, total_data, row):
        return ('EffectiveDate' in total_data and total_data['EffectiveDate'] and
                total_data['EffectiveDate'] != row['EffectiveDate'])

    def _csv_group_keys(self, row):
        return (
            row['EffectiveDate'], row['Location'], row['Tenancy'],
            row['Operating System'], row['Instance Type'], row['LeaseContractLength']
        )

    def _fieldnames(self):
        return (
            'Region', 'Tenancy', 'Platform', 'Instance Type', 'Term',
            'Payment Type', 'Upfront', 'Monthly'
        )

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

__ALL__ = [
    CloudCheckrAccounts,
    ComputeDetailsWarp,
    ComputeMigrationWarp,
    ComputeRIWarp,
    ComputeUnderutilizedWarp,
    ComputeUnderutilizedBreakdownWarp,
    DBDetailsWarp,
    DBIdleWarp,
    IAMUsersData,
    LBIdleWarp,
    RIPricingWarp,
    StorageDetachedWarp,
]
