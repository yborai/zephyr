import json
import math
import pandas as pd
import requests

from requests.auth import HTTPBasicAuth

from datetime import datetime
from urllib.parse import urlencode

from ..client import Client
from ..utils import first_of_previous_month, get_config_values, timed

class AlertLogic(Client):
    name = "AlertLogic"

    @classmethod
    def get_params(cls, acc_id, date):
        return dict(
            customer_id=acc_id,
            limit=500,
        )

    def __init__(self, config=None, log=None, **kwargs):
        if(config):
            super().__init__(config, log=log)
        self._AL_API_KEY = None

    @property
    def AL_API_KEY(self):
        if self._AL_API_KEY:
            return self._AL_API_KEY
        al_config_keys = ("AL_API_KEY", "AL_API_BASE")
        AL_API_KEY, AL_API_BASE = get_config_values("lw-al", al_config_keys, self.config)
        self._AL_API_KEY = AL_API_KEY
        self.AL_API_BASE = AL_API_BASE
        return self._AL_API_KEY

    def load_pages(self, url, timing=False, log=print):
        headers = {"Accept": "application/json"}
        auth = HTTPBasicAuth(self.AL_API_KEY, "")
        def time(func):
            if(timing):
                return timed(func, log=log)
            return func

        incidents = time(lambda: requests.get(
            url,
            headers=headers,
            auth=auth,
        ))()

    def get_account_by_slug(self, acc_short_name):
        raise NotImplementedError

    def get_month_timestamps(self, date):
        SEC_IN_DAY = 86400
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_timestamp = int(date_obj.timestamp())
        fopm_timestamp = int(first_of_previous_month(date_obj).timestamp())
        dates_in_month = list()
        for day in range(fopm_timestamp, date_timestamp, SEC_IN_DAY):
            dates_in_month.append(day)
        return dates_in_month

    def parse(self, json_string):
        raise NotImplementedError

    def request(self, account, date):
        al_id = self.get_account_by_slug(account)
        dates_in_month = get_month_timestamps(date)
        incidents = list()
        for day in dates_in_month:
            params = self.get_params(al_id)
            url = "".join([
                self.AL_API_BASE,
                self.uri,
                "?",
                urlencode(params),
                "&create_date=>{}".format(day+3600*5) # Adjust for timezone
            ])
            self.log.debug(url)
            response = self.load_pages(url, timing=True, log=self.log.info)
            incidents.append(incidents)
        return json.dumps(incidents)

