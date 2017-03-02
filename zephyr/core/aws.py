import io
import os
import sqlite3

import boto3
import pandas as pd

from warnings import warn

from botocore.exceptions import ClientError
from timeout_decorator import timeout, TimeoutError as TimeoutDecoratorError

from .ddh import DDH


TIMEOUT = 30

class SilenceExplicitly(object):
    """ Adapted from http://stackoverflow.com/a/5507784 """
    def __init__(self, errors, retval=None, handler=None):
        self.errors = errors
        self.retval = retval
        self.handler = handler
     
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if type(e) not in self.errors:
                    raise e
                if self.handler is not None:
                    self.handler(e, *args, **kwargs)
                return self.retval
        return wrapper


def aws_timeout_warning(exception, *args, **kwargs):
    warn("The call to AWS timed out.")

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

@SilenceExplicitly((TimeoutDecoratorError,), handler=aws_timeout_warning)
@timeout(TIMEOUT, use_signals=False)
def get_s3(s3, bucket, key):
    temp = io.BytesIO()
    try:
        s3.meta.client.download_fileobj(
            bucket,
            key,
            temp,
        )
    except ClientError as e:
        pass
    return temp.getvalue()

def get_session(key_id, secret):
    return boto3.session.Session(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
    )

@SilenceExplicitly((TimeoutDecoratorError,), handler=aws_timeout_warning)
@timeout(TIMEOUT, use_signals=False)
def put_s3(s3, filename, bucket, key):
    s3.meta.client.upload_file(filename, bucket, key)

def sdb_flatten(item):
    cells = item['Attributes']
    out = dict()
    for cell in cells:
        out[cell['Name']] = cell['Value']
    return out
