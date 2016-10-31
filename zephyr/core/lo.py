import sqlite3

import pandas as pd
import requests

from .ddh import DDH

def get_account_by_slug(slug, database):
    return pd.read_sql("""
        SELECT a.name AS slug, l.name AS lo_name
        FROM
            aws AS a LEFT OUTER JOIN
            projects AS p ON (p."Id" = a."Assoc_Project__c") LEFT OUTER JOIN
            logicops_accounts AS l ON (p.LogicOps_ID__c = l.id)
        WHERE a.name = '{slug}'
        """.format(slug=slug),
        database
    )["lo_name"][0]

def get_accounts(database, config):
    url_accts = "https://logicops.logicworks.net/api/v1/accounts/"
    username, password = config
    cookies = get_cookies(username, password)
    r = requests.get(url_accts, cookies=cookies, verify=False)
    accts = r.json()
    accounts = accts["accounts"]
    header = ["id", "name"]
    data = [[account[col] for col in header] for account in accounts]
    df = pd.DataFrame(data, columns=header)
    df.to_sql("logicops_accounts", database, if_exists="replace")

def get_cookies(username, password):
    url_auth = "https://logicops.logicworks.net"
    lo = dict(login=username, passphrase=password)
    r = requests.post(url_auth, data=lo, verify=False)
    return r.cookies
