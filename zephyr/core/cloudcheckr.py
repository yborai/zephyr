import json
import os

import pandas as pd
import requests

from urllib.parse import urlencode

from .utils import account_ids, timed

def cache(
        WarpClass,
        base,
        api_key,
        cc_name,
        date,
        cache_root,
        cache_dir,
        bucket,
        session,
        log=print
    ):
    params = WarpClass.get_params(api_key, cc_name, date)
    url = "".join([
        base,
        WarpClass.uri,
        "?",
        urlencode(params),
    ])
    log(url)
    folder = os.path.join(cache_root, cache_dir)
    response = load_pages(url, timing=True, log=log)
    cache_file = cache_path(folder, WarpClass.slug)
    os.makedirs(folder, exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(response, f)
    s3 = session.resource("s3")
    s3_key = cache_path(cache_dir, WarpClass.slug)
    s3.meta.client.upload_file(cache_file, bucket, s3_key)
    return json.dumps(response)

def cache_path(cache, filename):
    return os.path.join(cache, "{}.json".format(filename))

def get_accounts(database, config, log=None):
    base = "https://api.cloudcheckr.com/api/"
    uri_accts = "account.json/get_accounts_v2"
    api_key = config[0]
    params = dict(access_key=api_key)
    url = "".join([
        base,
        uri_accts,
        "?",
        urlencode(params),
    ])
    r = timed(lambda:requests.get(url), log=log)()
    accts = r.json()
    header = ["aws_account", "id", "name"]
    data = [[
            acct["aws_account_id"],
            acct["cc_account_id"],
            acct["account_name"],
        ]
        for acct in accts["accounts_and_users"]
    ]
    df = pd.DataFrame(data, columns=header)
    df.to_sql("cloudcheckr_accounts", database, if_exists="replace")

def get_account_by_slug(acc_short_name, database):
    return pd.read_sql("""
        SELECT a.name AS slug, c.name AS cc_name
        FROM
            aws AS a LEFT OUTER JOIN
            cloudcheckr_accounts AS c ON (c.aws_account = a."Acct_Number__c")
        WHERE a.name = '{slug}'
        """.format(slug=acc_short_name),
        database
    )["cc_name"][0]


def load_pages(url, timing=False, log=print):
    """
    Pagination
    """
    tmpl = "&next_token={token}"
    token = ""
    page_next = True
    out = list()
    def time(func):
        if(timing):
            return timed(func, log=log)
        return func

    while(page_next):
        url_cur = url
        if(token):
            url_cur = url + tmpl.format(token=token)
        resp = time(lambda:requests.get(url_cur))()
        obj = resp.json()
        page_next = obj.get("HasNext", False)
        token = ""
        if(page_next):
            token = obj["NextToken"]
        out.append(obj)
    return out
