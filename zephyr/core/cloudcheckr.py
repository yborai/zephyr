from .utils import timed

def load_pages(url, timing=False):
    """
    Pagination
    """
    tmpl = "&next_token={token}"
    token = ""
    page_next = True
    out = list()
    def time(func):
        if(timing):
            return timed(func)
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

def cache(url, cache, filename):
    print(url)
    return
    response = load_pages(url, timing=True)
    with open(os.path.join(cache_folder, filename + ".json"), "w") as f:
        json.dump(response, f)
    return response
