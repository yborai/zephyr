import os
import sqlite3

from . import aws
from .cc import calls as cc
from .lo import calls as lo
from .sf import calls as sf
from .client import Client
from .ddh import DDH
from .utils import get_config_values

class LWProjects(Client):

    def cache_policy(self, expired=False):
        """
        Obtains a local database connection,
        retrieving data from S3 or Salesforce as necessary.
        """
        zdb = self.ZEPHYR_DATABASE
        db = os.path.join(self.ZEPHYR_CACHE_ROOT, zdb)
        db_dir = os.path.dirname(db)
        os.makedirs(db_dir, exist_ok=True)
        db_exists = os.path.isfile(db)
        # If a local cache exists and it is not expired then use that.
        if(db_exists and not expired):
            self.log.info("Database exists locally.")
            return sqlite3.connect(db)
        s3 = self.s3  # This is a bit kludgy. TODO: Fix this.
        """
        If a local cache does not exist and the cache is not expired
        then check S3 for a backup.
        """
        if(not db_exists and not expired):
            self.log.info("Checking S3 for cached copy of database.")
            cache_s3 = aws.get_s3(s3, self.ZEPHYR_S3_BUCKET, zdb)
            if(cache_s3):
                self.log.info("Downloaded cached database from S3.")
                with open(db, "wb") as cache_fd:
                    cache_fd.write(cache_s3)
                return self.database
            self.log.info("Cached database not found on S3.")
        """
        If there is no local database, no S3 cache or the cache is expired
        then get metadata from Logicops and Salesforce.
        """
        self.log.info("Loading account metadata from Salesforce.")
        sf.SalesForceAccounts(config=self.config, log=self.log).request()
        sf.SalesForceAWSAccounts(config=self.config, log=self.log).request()
        sf.SalesForceProjects(config=self.config, log=self.log).request()
        self.log.info("Loading account metadata from Cloudcheckr.")
        cc.CloudCheckrAccounts(self.config, log=self.log).request()
        self.log.info("Loading account metadata from Logicops.")
        lo.LogicopsAccounts(self.config).request()
        self.log.info("Caching account metadata in S3.")
        aws.put_s3(s3, db, self.ZEPHYR_S3_BUCKET, zdb)
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
        FROM sf_accounts AS a
            LEFT OUTER JOIN sf_projects AS p ON (a.Id=p.Account__c)
            LEFT OUTER JOIN sf_aws AS aws ON (p.Id=aws.Assoc_Project__c)
            LEFT OUTER JOIN lo_accounts AS lo ON (p.LogicOps_ID__c=lo.id)
        WHERE 1
            AND aws.Name IS NOT NULL
        ORDER BY client
        LIMIT 200
        """
        return DDH.read_sql(query, self.database)
