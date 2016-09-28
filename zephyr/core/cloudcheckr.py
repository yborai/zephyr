import json
import os

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
        WarpClass.get_uri(),
        "?",
        urlencode(params),
    ])
    log(url)
    folder = os.path.join(cache_root, cache_dir)
    response = load_pages(url, timing=True, log=log)
    cache_file = cache_path(folder, WarpClass.get_slug())
    os.makedirs(folder, exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(response, f)
    s3 = session.resource('s3')
    s3_key = cache_path(cache_dir, WarpClass.get_slug())
    s3.meta.client.upload_file(cache_file, bucket, s3_key)
    return json.dumps(response)

def cache_path(cache, filename):
    return os.path.join(cache, "{}.json".format(filename))

def get_cloudcheckr_name(acc_short_name, accounts_json):
    accounts = account_ids(accounts_json)
    return accounts[acc_short_name]["cc"]["name"]

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
