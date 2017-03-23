import csv
import json

import pandas as pd
import requests

from datetime import datetime
from itertools import groupby
from urllib.parse import urlencode

from ..ddh import DDH
from ..utils import timed
from . import client as cc

class CloudCheckrAccounts(cc.CloudCheckr):
    uri = "account.json/get_accounts_v2"

    def request(self):
        params = dict(access_key=self.CC_API_KEY)
        url = "".join([
            self.CC_API_BASE,
            self.uri,
            "?",
            urlencode(params),
        ])
        self.log.debug(url)
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
        df.to_sql("cc_accounts", self.database, if_exists="replace")

class ComputeDetailsWarp(cc.CloudCheckr):
    key = "Ec2Instances"
    slug = "compute-details"
    uri = "inventory.json/get_resources_ec2_details_V3"
    header = (
            "InstanceId",
            "InstanceName",
            "Region",
            "InstanceType",
            "LaunchTime",
            "PrivateIpAddress",
            "PricingPlatform",
            "Tenancy",
            "Environment",
            "Status",
        )

    def __init__(self, config=None, log=None, **kwargs):
        if(config):
            super().__init__(config=config, log=log, **kwargs)
        self.all_tags = kwargs.get("all_tags")

    def parse(self, json_string):
        results = json.loads(json_string)
        items = self.merge(results)
        if self.all_tags:
            self.header = self.header[:-2] + ("ResourceTags",) + self.header[-2:]

        data = list()
        for row in items:
            filtered = self._filter_row(row)
            data.append([filtered.get(col, "") for col in self.header])
        self.data = data

    def _filter_row(self, row):
        if "ResourceTags" not in row:
            return row
        for tag in row["ResourceTags"]:
            if tag["Key"] != "lw:environment":
                continue
            row["Environment"] = tag["Value"]
        return row

    def _items_from_pages(self, page):
        return page["Ec2Instances"]

class ComputeMigrationWarp(cc.CloudCheckrBPC):
    bpc_id = 240
    slug = "compute-migration"
    header = (
            "Instance ID",
            "Instance Name",
            "Region",
            "Recommendation",
            "On-Demand Current Monthly Cost",
            "Cost for Recommended",
            "Yearly Savings",
            "Platform",
            "vCPU for current",
            "vCPU for next gen",
            "Memory for current",
            "Memory for next gen",
        )

class ComputeRIWarp(cc.CloudCheckrBPC):
    bpc_id = 190
    slug = "compute-ri"
    header = (
            "Number",
            "Instance Type",
            "AZ",
            "Platform",
            "Commitment Type",
            "Tenancy",
            "Upfront RI Cost",
            "Reserved Monthly Cost",
            "On-Demand Monthly Cost",
            "Total Savings",
        )

class ComputeUnderutilizedWarp(cc.CloudCheckrBPC):
    bpc_id = 68
    slug = "compute-underutilized"
    header =  (
            "Instance ID",
            "Instance Name",
            "Average CPU Util",
            "Predicted Monthly Cost",
            "Region",
        )

class DBDetailsWarp(cc.CloudCheckr):
    slug = "db-details"
    uri = "inventory.json/get_resources_rds_details"
    header = (
        "DbInstanceId",
        "DbInstanceName",
        "MonthlyCost",
        "RegionName",
        "DbInstanceClass",
        "Engine",
        "EngineVersion",
        "LicenseModel",
        "AllocatedStorageGB",
        "FreeStorageSpaceBytes",
        "Endpoint",
        "BackupRetentionPeriod",
    )

    def _items_from_pages(self, page):
        return page["RdsDbInstances"]

class DBIdleWarp(cc.CloudCheckrBPC):
    bpc_id = 134
    slug = "db-idle"
    header = (
        "DB Instance",
        "Average Read IOPS",
        "Average Write IOPS",
        "Predicted Monthly Cost",
        "Region",
    )

class IAMUsersData(cc.CloudCheckr):
    slug = "iam-users"
    uri = "inventory.json/get_resources_iam_users"
    header = (
        "Username",
        "Has MFA",
        "Console Last Used",
        "Access Key 1 Last Used",
        "Access Key 2 Last Used",
    )

    def parse(self, json_string):
        results = json.loads(json_string)
        items = self.merge(results)
        self.data = [
            [
                user["UserName"],
                user["HasMfa"],
                user["LastUsed"],
                user["UserCredential"]["AccessKey1LastUsedDate"],
                user["UserCredential"]["AccessKey2LastUsedDate"],
            ]
                for user in items
        ]

    def _items_from_pages(self, page):
        return page["IamUsersDetails"]

class LBIdleWarp(cc.CloudCheckrBPC):
    bpc_id = 126
    slug = "lb-idle"
    uri = "best_practice.json/get_best_practices"
    header = (
        "Load Balancer",
        "Average Hourly Request Count",
        "Predicted Monthly Cost",
    )

class StorageDetachedWarp(cc.CloudCheckrBPC):
    bpc_id = 1
    slug = "storage-detached"
    header = (
        "Volume ID",
        "Size",
        "Predicted Monthly Cost",
        "EC2 Instance",
        "Region",
    )


__ALL__ = [
    CloudCheckrAccounts,
    ComputeDetailsWarp,
    ComputeMigrationWarp,
    ComputeRIWarp,
    ComputeUnderutilizedWarp,
    DBDetailsWarp,
    DBIdleWarp,
    IAMUsersData,
    LBIdleWarp,
    StorageDetachedWarp,
]
