import os
import sqlite3

from datetime import datetime

from . import aws
from .ddh import DDH
from .utils import get_config_values

class Client(object):
    def __init__(self, config):
        aws_config_keys = ("s3_bucket", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")
        bucket, key_id, secret = get_config_values("lw-aws", aws_config_keys, config)
        zephyr_config_keys = ("cache", "database")
        cache_root, db = [
            os.path.expanduser(path)
            for path in get_config_values("zephyr", zephyr_config_keys, config)
        ]
        self.bucket = bucket
        self.cache_root = cache_root
        self.config = config
        self.database = sqlite3.connect(os.path.join(cache_root, db))
        self.db = db
        self.key_id = key_id
        self.secret = secret
        self.session = aws.get_session(key_id, secret)
        self.s3 = self.session.resource("s3")

    def cache(self, response, cache_key, log=None):
        cache_local = os.path.join(self.cache_root, cache_key)
        log.info("Caching {} response locally.".format(self.name))
        with open(cache_local, "w") as f:
            f.write(response)
        log.info("Caching {} response in S3.".format(self.name))
        self.s3.meta.client.upload_file(cache_local, self.bucket, cache_key)

    def cache_policy(self, account, date, cache_file, expired, log=None):
        # If cache_file is specified then use that
        if(cache_file):
            log.info("Using specified cached response: {cache}".format(cache=cache_file))
            with open(cache_file, "r") as f:
                return f.read()
        # If no date is given then default to the first of last month.
        now = datetime.now()
        if(not date):
            date = datetime(year=now.year, month=now.month-1, day=1).strftime("%Y-%m-%d")
        # If local exists and expired is false then use the local cache
        cache_key = self.cache_key(account, date)
        cache_local = os.path.join(self.cache_root, cache_key)
        os.makedirs(os.path.dirname(cache_local), exist_ok=True)
        cache_local_exists = os.path.isfile(cache_local)
        if(cache_local_exists and not expired):
            log.info("Using cached response: {cache}".format(cache=cache_local))
            with open(cache_local, "r") as f:
                return f.read()
        # If local does not exist and expired is false then check s3
        cache_s3 = self.get_object_from_s3(cache_key)
        if(cache_s3 and not expired):
            log.info("Using cached response from S3.")
            with open(cache_local, "wb") as cache_fd:
                cache_fd.write(cache_s3)
            return cache_s3.decode("utf-8")
        # If we are this far then contact the API and cache the result
        log.info("Retrieving data from {}.".format(self.name))
        response = self.request(account, date, log=log)
        self.cache(response, cache_key, log=log)
        return response

    def get_object_from_s3(self, cache_key):
        cache_local = os.path.join(self.cache_root, cache_key)
        session = aws.get_session(self.key_id, self.secret)
        return aws.get_object_from_s3(self.bucket, cache_key, self.s3)

    def get_slugs(self):
        query = 'SELECT "Name" AS slug FROM aws ORDER BY "Name"'
        slugs = DDH.read_sql(query, self.database)
        return list(zip(*slugs.data))[0]

    def slug_valid(self, slug):
        return True

    def to_ddh(self):
        return DDH(header=self.header, data=self.data)