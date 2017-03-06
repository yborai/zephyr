import os
import sqlite3

import pandas as pd

from datetime import datetime
from shutil import rmtree

from timeout_decorator import timeout

from . import aws
from .ddh import DDH
from .utils import get_config_values

class Client(object):
    @classmethod
    def cache_key(cls, account, date):
        month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        filename = "{slug}.json".format(slug=cls.slug)
        return os.path.join(account, month, filename)

    def __init__(self, config, log=None):
        zephyr_config_keys = ("ZEPHYR_CACHE_ROOT", "ZEPHYR_DATABASE")
        cache_root, db = [
            os.path.expanduser(path)
            for path in get_config_values("zephyr", zephyr_config_keys, config)
        ]
        self._database = None
        self._ddh = None
        self._s3 = None
        self.AWS_ACCESS_KEY_ID = None
        self.AWS_SECRET_ACCESS_KEY = None
        self.ZEPHYR_CACHE_ROOT = cache_root
        self.ZEPHYR_DATABASE = db
        self.ZEPHYR_S3_BUCKET = None
        self.config = config
        self.log = log
        self.session = None

    @property
    def database(self):
        if(self._database):
            return self._database
        db_path = os.path.join(
            self.ZEPHYR_CACHE_ROOT,
            self.ZEPHYR_DATABASE
        )
        db_exists = os.path.isfile(db_path)
        self._database = sqlite3.connect(db_path)
        return self._database

    @property
    def ddh(self):
        return self._ddh

    @ddh.setter
    def ddh(self, value):
        self._ddh = value

    @property
    def s3(self):
        if self._s3:
            return self._s3
        aws_config_keys = (
            "ZEPHYR_S3_BUCKET", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"
        )
        bucket, key_id, secret = get_config_values(
            "lw-aws", aws_config_keys, self.config
        )
        self.AWS_ACCESS_KEY_ID = key_id
        self.AWS_SECRET_ACCESS_KEY = secret
        self.ZEPHYR_S3_BUCKET = bucket
        self.session = aws.get_session(key_id, secret)
        self._s3 = self.session.resource("s3")
        return self._s3

    def cache(self, response, cache_key):
        cache_local = os.path.join(self.ZEPHYR_CACHE_ROOT, cache_key)
        self.log.info("Caching {api} response for {call} locally.".format(
            api=self.name,
            call=self.slug,
        ))
        with open(cache_local, "w") as f:
            f.write(response)
        self.log.info("Caching {api} response for {call} in S3.".format(
            api=self.name,
            call=self.slug,
        ))
        aws.put_s3(self.s3, cache_local, self.ZEPHYR_S3_BUCKET, cache_key)

    def cache_policy(self, account, date, expired):
        # If local exists and expired is false then use the local cache
        cache_key = self.cache_key(account, date)
        cache_local = os.path.join(self.ZEPHYR_CACHE_ROOT, cache_key)
        os.makedirs(os.path.dirname(cache_local), exist_ok=True)
        cache_local_exists = os.path.isfile(cache_local)
        if(cache_local_exists and not expired):
            self.log.info("Using cached response: {cache}".format(cache=cache_local))
            with open(cache_local, "r") as f:
                return f.read()
        # If local does not exist and expired is false then check s3
        cache_s3 = self.get_s3(cache_key)
        if(cache_s3 and not expired):
            self.log.info("Using cached response for {} from S3.".format(self.slug))
            with open(cache_local, "wb") as cache_fd:
                cache_fd.write(cache_s3)
            return cache_s3.decode("utf-8")
        # If we are this far then contact the API and cache the result
        self.log.info("Retrieving data for {call} from {api}.".format(
            api=self.name,
            call=self.slug,
        ))
        response = self.request(account, date)
        self.cache(response, cache_key)
        return response

    def clear_cache_s3(self, account, month):
        # Lists objects in the desired directory
        cache_s3 = os.path.join(account, month)
        objects = self.s3.meta.client.list_objects(
            Bucket=self.ZEPHYR_S3_BUCKET,
            Prefix="{}".format(cache_s3)
        )

        # Delete files from folder in S3 if they exist
        if "Contents" not in objects:
            return
        count = 0
        for obj in objects["Contents"]:
            self.log.debug("Deleting {}".format(obj["Key"]))
            self.s3.meta.client.delete_object(
                Bucket=self.ZEPHYR_S3_BUCKET,
                Key=obj["Key"]
            )
            count += 1
        self.log.info(
            "Deleted {count} files from {cache_s3} in S3".format(
                count=count, cache_s3=cache_s3)
        )

    def clear_cache_local(self, account, month):
        # Delete directory locally
        cache_local = os.path.join(self.ZEPHYR_CACHE_ROOT, account, month)
        if not os.path.exists(os.path.expanduser(cache_local)):
            return
        count = len(os.listdir(cache_local))
        rmtree(cache_local)
        self.log.info(
            "Deleted {count} files from {cache_local}.".format(
                count=count, cache_local=cache_local)
        )

    def get_account_by_slug(self, slug):
        raise NotImplementedError

    def get_s3(self, cache_key):
        #s3 = self.s3  # This is a bit kludgy. TODO: Fix this.
        return aws.get_s3(self.s3, self.ZEPHYR_S3_BUCKET, cache_key)

    def get_slugs(self):
        query = ("""
            SELECT aws."Name" AS slug
            FROM
                sf_projects AS p LEFT OUTER JOIN
                sf_aws AS aws ON (p.Id=aws.Assoc_Project__c)
            WHERE aws."Name" IS NOT NULL
            ORDER BY aws."Name"
        """)
        slugs = DDH.read_sql(query, self.database)
        return list(zip(*slugs.data))[0]

    def to_ddh(self):
        self.ddh = DDH(header=self.header, data=self.data)
        return self._ddh

    def to_sql(self, name, con):
        ddh = self.to_ddh()
        data = [[str(cell) for cell in row] for row in ddh.data]
        df = pd.DataFrame(data, columns=self.ddh.header)
        df.to_sql(name, con)
