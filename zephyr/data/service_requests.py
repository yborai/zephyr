import json
import os
import sqlite3

import requests

from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlencode

from ..core import aws, lo
from ..core.ddh import DDH
from ..core.utils import ZephyrException
from .common import get_config_values

def cache_key(account, date):
    month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
    filename = "service-requests.{date}.json".format(date=date)
    return os.path.join(account, month, filename)

class ServiceRequests(object):
    base = "https://logicops.logicworks.net/api/v1/"
    uri = "sr-filter"

    header_hash = OrderedDict([
        ("summary", "Summary"),
        ("status", "Status"),
        ("severity", "Severity"),
        ("area", "Area"),
        ("created_date", "Created Date"),
        ("created_by", "Created By"),
    ])

    @classmethod
    def cache(cls, account, date, cache_file, expired, config=None, log=None):
        #
        #
        # If cache_file is specified then use that
        if(cache_file):
            log.info("Using specified cached response: {cache}".format(cache=cache_file))
            with open(cache_file, "r") as f:
                return f.read()
        zephyr_config_keys = ("cache", "database")
        cache_root, db = [
            os.path.expanduser(path)
            for path in get_config_values("zephyr", zephyr_config_keys, config)
        ]
        database = sqlite3.connect(os.path.join(cache_root, db))
        #
        #
        # If no date is given then default to the first of last month.
        now = datetime.now()
        if(not date):
            date = datetime(year=now.year, month=now.month-1, day=1).strftime("%Y-%m-%d")
        month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        # If local exists and expired is false then use the local cache
        cache_key_ = cache_key(account, date)
        cache_local = os.path.join(cache_root, cache_key_)
        os.makedirs(os.path.dirname(cache_local), exist_ok=True)
        cache_local_exists = os.path.isfile(cache_local)
        if(cache_local_exists and not expired):
            log.info("Using cached response: {cache}".format(cache=cache_local))
            with open(cache_local, "r") as f:
                return f.read()
        # If local does not exist and expired is false then check s3
        aws_config_keys = ("s3_bucket", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")
        bucket, key_id, secret = get_config_values("lw-aws", aws_config_keys, config)
        session = aws.get_session(key_id, secret)
        s3 = session.resource("s3")
        cache_s3 = aws.get_object_from_s3(bucket, cache_key_, s3)
        if(cache_s3 and not expired):
            log.info("Using cached response from S3.")
            with open(cache_local, "wb") as cache_fd:
                cache_fd.write(cache_s3)
            return cache_s3.decode("utf-8")
        today = now.strftime("%Y-%m-%d")
        # If no cache exists and the report is not for today then break.
        if(date != today and not expired):
            raise ZephyrException(
                "Cache not found for date {}. "
                "Specify today's date to run this report "
                "for current Service Requests.".format(date)
        )
        # If we are this far then contact the API and cache the result
        lo_config_keys = ("login", "passphrase")
        user, passwd = get_config_values("lw-lo", lo_config_keys, config)
        cookies = lo.get_cookies(user, passwd)
        lo_acct = lo.get_account_by_slug(account, database)
        log.info("Loading service-requests from Logicops.")
        response = ServiceRequests.read_srs(lo_acct, cookies=cookies)
        log.info("Caching service-requests response locally.")
        with open(cache_local, "w") as f:
            f.write(response)
        log.info("Caching service-requests response in S3.")
        s3.meta.client.upload_file(cache_local, bucket, cache_key_)
        return response

    @classmethod
    def read_srs(cls, account, cookies=None):
        params = {
            "team_options[0]" : "_all_",
            "assigned_to_options[0]" : "_all_",
            "group_options[0]" : "_all_",
            "area_options[0]" : "_all_",
            "status_options[0]" : "_all_",
            "severity_options[0]" : "_all_",
            "account_options[0]" : account,
        }
        url = "".join([
            cls.base,
            cls.uri,
            "?",
            urlencode(params),
        ])
        r = requests.get(url, cookies=cookies, verify=False)
        return r.content.decode("utf-8")

    def __init__(self, json_string=None):
        self.response = json.loads(json_string)
        header_raw = self.response["header"]
        data_raw = self.response["data"]

        self.header = list(self.header_hash.values())
        self.column_indexes = [header_raw.index(key) for key in list(self.header_hash.keys())]
        self.data = [[row[index] for index in self.column_indexes] for row in data_raw]

    def to_ddh(self):
        header = self.header
        data = self.data

        return DDH(header=header, data=data)


