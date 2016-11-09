import os
import sqlite3

from . import aws, cloudcheckr as cc, lo, sf
from .ddh import DDH

def get_local_db_connection(
    cachedir, expired,
    log=None, aws_config=None, cc_config=None, lo_config=None, sf_config=None
):
    """
    Obtains a local database connection,
    retrieving data from S3 or Salesforce as necessary.
    """
    metadir = os.path.join(cachedir, "meta/")
    os.makedirs(metadir, exist_ok=True)
    s3_key = "meta/local.db"
    db = os.path.join(cachedir, s3_key)
    db_exists = os.path.isfile(db)
    # If a local cache exists and it is not expired then use that.
    if(db_exists and not expired):
        log.info("Database exists locally.")
        return sqlite3.connect(db)
    aws_key_id, aws_secret, aws_bucket = aws_config
    session = aws.get_session(aws_key_id, aws_secret)
    s3 = session.resource("s3")
    """
    If a local cache does not exist and the cache is not expired
    then check S3 for a backup.
    """
    if(not db_exists and not expired):
        log.info("Checking S3 for cached copy of database.")
        cache_s3 = aws.get_object_from_s3(aws_bucket, s3_key, s3)
        if(cache_s3):
            log.info("Downloaded cached database from S3.")
            with open(db, "wb") as cache_fd:
                cache_fd.write(cache_s3)
            return sqlite3.connect(db)
        log.info("Cached database not found on S3.")
    """
    If there is no local database, no S3 cache or the cache is expired
    then get metadata from Logicops and Salesforce.
    """
    log.info("Loading account metadata from Salesforce.")
    database = sf.cache(db, config=sf_config)
    database = sqlite3.connect(db)
    log.info("Loading account metadata from Cloudcheckr.")
    cc.get_accounts(database, config=cc_config, log=log.info)
    log.info("Loading account metadata from Logicops.")
    lo.get_accounts(database, config=lo_config)
    log.info("Caching account metadata in S3.")
    s3.meta.client.upload_file(db, aws_bucket, s3_key)
    return database

def get_all_projects(database):
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
    return DDH.read_sql(query, database)

