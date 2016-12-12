import os
import sqlite3

from . import aws, sf
from .cc import calls as cc
from .lo import client as lo
from .client import Client
from .ddh import DDH
from .utils import get_config_values

class LWProjects(Client):
    def __init__(self, config):
        super().__init__(config)
        sf_config_keys = ("SF_USERNAME", "SF_PASSWD", "SF_TOKEN")
        sf_config = get_config_values("lw-sf", sf_config_keys, config)
        self.sf_config = sf_config

    def cache_policy(self, expired=False, log=None):
        """
        Obtains a local database connection,
        retrieving data from S3 or Salesforce as necessary.
        """
        metadir = os.path.join(self.cache_root, "meta/")
        os.makedirs(metadir, exist_ok=True)
        s3_key = "meta/local.db"
        db = os.path.join(self.cache_root, self.db)
        db_exists = os.path.isfile(db)
        # If a local cache exists and it is not expired then use that.
        if(db_exists and not expired):
            log.info("Database exists locally.")
            return sqlite3.connect(db)
        session = aws.get_session(self.key_id, self.secret)
        s3 = session.resource("s3")
        """
        If a local cache does not exist and the cache is not expired
        then check S3 for a backup.
        """
        if(not db_exists and not expired):
            log.info("Checking S3 for cached copy of database.")
            cache_s3 = aws.get_object_from_s3(self.bucket, s3_key, s3)
            if(cache_s3):
                log.info("Downloaded cached database from S3.")
                with open(db, "wb") as cache_fd:
                    cache_fd.write(cache_s3)
                return self.database
            log.info("Cached database not found on S3.")
        """
        If there is no local database, no S3 cache or the cache is expired
        then get metadata from Logicops and Salesforce.
        """
        log.info("Loading account metadata from Salesforce.")
        sf.cache(db, config=self.sf_config)
        log.info("Loading account metadata from Cloudcheckr.")
        cc.CloudCheckrAccounts(self.config, log=log).request()
        log.info("Loading account metadata from Logicops.")
        lo.LogicopsAccounts(self.config).request()
        log.info("Caching account metadata in S3.")
        s3.meta.client.upload_file(db, self.bucket, s3_key)
        return self.database

    def get_all_projects(self):
        query = """
        SELECT
            a.Name AS client,
            a.Type AS type,
            p.Name AS project,
            p.Dynamics_ID__c AS dynamics,
            p.JIRAKey__c AS jira,
            p.LogicOps_ID__c AS logicops,
            lo.name AS logicops_name,
            p.Planned_Spend__c AS planned_spend,
            aws.Name AS slug,
            aws.Acct_Number__c AS aws_account,
            aws.Cloudcheckr_ID__c AS cloudcheckr_id,
            aws.Cloudcheckr_Name__c AS cloudcheckr_name,
            aws.Bitdefender_ID__c AS bitdefender
        FROM accounts AS a
            LEFT OUTER JOIN projects AS p ON (a.Id=p.Account__c)
            LEFT OUTER JOIN aws ON (p.Id=aws.Assoc_Project__c)
            LEFT OUTER JOIN logicops_accounts as lo ON (p.LogicOps_ID__c=lo.id)
        WHERE 1
            AND aws.Name IS NOT NULL
        ORDER BY client
        LIMIT 200
        """
        return DDH.read_sql(query, self.database)
