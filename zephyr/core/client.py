import os
import sqlite3

from . import aws
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

    def cache(self, response, cache_key, log=None):
        cache_local = os.path.join(self.cache_root, cache_key)
        log.info("Caching {} response locally.".format(self.name))
        with open(cache_local, "w") as f:
            f.write(response)
        log.info("Caching {} response in S3.".format(self.name))
        # Save a copy the response on S3
        s3 = self.session.resource("s3")
        s3.meta.client.upload_file(cache_local, self.bucket, cache_key)

    def get_object_from_s3(self, cache_key):
        cache_local = os.path.join(self.cache_root, cache_key)
        session = aws.get_session(self.key_id, self.secret)
        s3 = session.resource("s3")
        return aws.get_object_from_s3(self.bucket, cache_key, s3)
