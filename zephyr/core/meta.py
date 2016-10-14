import io
import os

import sqlite3

from . import aws
from . import sf
from .ddh import DDH

def get_local_db_connection(cachedir, expired, log=None, aws_config=None, sf_config=None):
    """
    Obtains a local database connection,
    retrieving data from S3 or Salesforce as necessary.
    """
    aws_key_id, aws_secret, aws_bucket = aws_config
    metadir = os.path.join(cachedir, "meta/")
    os.makedirs(metadir, exist_ok=True)
    s3_key = "meta/local.db"
    db = os.path.join(cachedir, s3_key)
    session = aws.get_session(aws_key_id, aws_secret)
    db_exists = os.path.isfile(db)
    # If a local cache exists and it is not expired then use that.
    if(db_exists and not expired):
        log.info("Database exists locally.")
        return sqlite3.connect(db)
    s3 = session.resource("s3")
    """
    If a local cache does not exist and the cache is not expired
    then check S3 for a backup.
    """
    if(not db_exists and not expired):
        log.info("Checking S3 for cached copy of database.")
        session = aws.get_session(aws_key_id, aws_secret)
        cache_temp = io.BytesIO()
        try:
            s3.meta.client.download_fileobj(
                aws_bucket,
                s3_key,
                cache_temp
            )
        except ClientError as e:
            log.info("Cached database not found on S3.")
            pass
        cache_s3 = cache_temp.getvalue()
        if(cache_s3):
            log.info("Downloaded cached database from S3.")
            with open(db, "wb") as cache_fd:
                cache_fd.write(cache_s3)
            return sqlite3.connect(db)
    """
    If there is no local database, no S3 cache or the cache is expired
    then get metadata from Salesforce.
    """
    log.info("Loading account metadata from Salesforce.")
    database = sf.cache(db, config=sf_config)
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
        p.Planned_Spend__c AS planned_spend,
        aws.Name AS slug,
        aws.Acct_Number__c AS aws_account,
        aws.Cloudcheckr_ID__c AS cloudcheckr_id,
        aws.Cloudcheckr_Name__c AS cloudcheckr_name,
        aws.Bitdefender_ID__c AS bitdefender
    FROM accounts AS a
        LEFT OUTER JOIN projects AS p ON (a.Id=p.Account__c)
        LEFT OUTER JOIN aws ON (p.Id=aws.Assoc_Project__c)
    WHERE 1
        AND aws.Name IS NOT NULL
    ORDER BY client
    LIMIT 200
    """
    return DDH.read_sql(query, database)

