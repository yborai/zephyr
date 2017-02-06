import os
import sqlite3

import pandas as pd

from datetime import datetime
from shutil import rmtree

from . import aws
from .ddh import DDH
from .utils import first_of_previous_month, get_config_values

class Client(object):
    @classmethod
    def cache_key(cls, account, date):
        month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        filename = "{slug}.json".format(slug=cls.slug)
        return os.path.join(account, month, filename)

    def __init__(self, config):
        aws_config_keys = ("ZEPHYR_S3_BUCKET", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")
        bucket, key_id, secret = get_config_values("lw-aws", aws_config_keys, config)
        zephyr_config_keys = ("ZEPHYR_CACHE_ROOT", "ZEPHYR_DATABASE")
        cache_root, db = [
            os.path.expanduser(path)
            for path in get_config_values("zephyr", zephyr_config_keys, config)
        ]
        self.ZEPHYR_S3_BUCKET = bucket
        self.ZEPHYR_CACHE_ROOT = cache_root
        self.config = config
        self.database = sqlite3.connect(os.path.join(cache_root, db))
        self.ZEPHYR_DATABASE = db
        self.AWS_ACCESS_KEY_ID = key_id
        self.AWS_SECRET_ACCESS_KEY = secret
        self.session = aws.get_session(key_id, secret)
        self.s3 = self.session.resource("s3")

    def cache(self, response, cache_key, log=None):
        cache_local = os.path.join(self.ZEPHYR_CACHE_ROOT, cache_key)
        log.info("Caching {} response locally.".format(self.name))
        with open(cache_local, "w") as f:
            f.write(response)
        log.info("Caching {} response in S3.".format(self.name))
        self.s3.meta.client.upload_file(cache_local, self.ZEPHYR_S3_BUCKET, cache_key)

    def cache_policy(self, account, date, expired, log=None):
        # If no date is given then default to the first of last month.
        if(not date):
            date = first_of_previous_month().strftime("%Y-%m-%d")
        # If local exists and expired is false then use the local cache
        cache_key = self.cache_key(account, date)
        cache_local = os.path.join(self.ZEPHYR_CACHE_ROOT, cache_key)
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

    def clear_cache_s3(self, account, month, log=None):
        #Lists objects in the desired directory
        cache_s3 = os.path.join(account, month)
        objects = self.s3.meta.client.list_objects(
            Bucket=self.ZEPHYR_S3_BUCKET,
            Prefix="{}".format(cache_s3)
        )

        #Delete files from folder in S3 if they exist
        if "Contents" not in objects:
            return
        count = 0
        for obj in objects["Contents"]:
            log.debug("Deleting {}".format(obj["Key"]))
            self.s3.meta.client.delete_object(
                Bucket=self.ZEPHYR_S3_BUCKET,
                Key=obj["Key"]
            )
            count += 1
        log.info(
            "Deleted {count} files from {cache_s3} in S3".format(
                count=count, cache_s3=cache_s3)
        )

    def clear_cache_local(self, account, month, log=None):
        #Delete directory locally
        cache_local = os.path.join(self.ZEPHYR_CACHE_ROOT, account, month)
        if not os.path.exists(os.path.expanduser(cache_local)):
            return
        count = len(os.listdir(cache_local))
        rmtree(cache_local)
        log.info(
            "Deleted {count} files from {cache_local}.".format(
                count=count, cache_local=cache_local)
        )

    def get_object_from_s3(self, cache_key):
        cache_local = os.path.join(self.ZEPHYR_CACHE_ROOT, cache_key)
        session = aws.get_session(self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY)
        return aws.get_object_from_s3(self.ZEPHYR_S3_BUCKET, cache_key, self.s3)

    def get_slugs(self):
        query = ("""
            SELECT aws."Name" AS slug
            FROM
                projects AS p LEFT OUTER JOIN
                aws ON (p.Id=aws.Assoc_Project__c)
            WHERE aws."Name" IS NOT NULL
            ORDER BY aws."Name"
        """)
        slugs = DDH.read_sql(query, self.database)
        return list(zip(*slugs.data))[0]

    def slug_valid(self, slug):
        return True

    def to_ddh(self):
        return DDH(header=self.header, data=self.data)

    def to_sql(self, name, con):
        ddh = self.to_ddh()
        data = [[str(cell) for cell in row] for row in ddh.data]
        df = pd.DataFrame(data, columns=self.ddh.header)
        df.to_sql(name, con)
