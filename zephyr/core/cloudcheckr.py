import json
import os

import requests

from .utils import account_ids, timed

def cache(url, cache, filename, log):
    response = load_pages(url, timing=True, log=log)
    with open(os.path.join(cache, filename + ".json"), "w") as f:
        json.dump(response, f)
    return json.dumps(response)

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
