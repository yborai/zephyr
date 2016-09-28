import os
import sqlite3

import boto3
import pandas as pd

from .ddh import DDH

def get_accounts_aws(key_id, secret):
    sdb = boto3.client(
        'sdb',
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
    )
    select = (
        "SELECT client, acc_short_name "
        "FROM insite "
        "WHERE acc_short_name like '%' "
        "ORDER BY acc_short_name "
    )
    response = sdb.select(SelectExpression=select)
    items = response['Items']
    client_data = {item['Name'] : sdb_flatten(item) for item in items}
    header = ['acc_short_name', 'account_id', 'client']
    def row(item):
        item_dict = sdb_flatten(item)
        return (
            item_dict['acc_short_name'],
            item['Name'],
            item_dict['client']
        )
    data = [row(item) for item in items]
    return DDH(header=header, data=data)

def get_accounts(key_id, secret, cache, log):
    db = os.path.join(cache, "local.db")
    db_exists = os.path.isfile(db)
    con = sqlite3.connect(db)
    if(not db_exists):
        # If the local cache does not exist then retrieve from S3
        # TODO: Add S3 cache functionality
        # If the S3 cache does not exist then
        #  * retrieve from SDB
        #  * save locally
        #  * TODO: upload to S3
        log.info("Reading accounts from SDB.")
        accts = get_accounts_aws(key_id, secret)
        df = pd.DataFrame(accts.data, columns=accts.header)
        df.to_sql("clients", con)
    else:
        log.info("Reading accounts from cache.")
        query = "SELECT acc_short_name, account_id, client from clients"
        accts = DDH.read_sql(query, con)

    return accts

def get_session(key_id, secret):
    return boto3.session.Session(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
    )

def sdb_flatten(item):
    cells = item['Attributes']
    out = dict()
    for cell in cells:
        out[cell['Name']] = cell['Value']
    return out

def upload_file(file_path, bucket, key, session):
    s3 = session.resource('s3')
    s3.meta.client.upload_file(file_path, bucket, key)

