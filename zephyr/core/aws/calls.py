import datetime
import io

import pandas as pd
import requests

from ..utils import timed
from .client import AWSPricingAPI

class AWSEC2Pricing(AWSPricingAPI):
    uri = "AmazonEC2/current/index.csv"
    slug = "ec2-pricing"

    def cache_policy(self, expired):
        query = """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name='cache_log'
        """
        exists = pd.read_sql(query, self.database)
        if len(exists) and not expired:
            return pd.read_sql("""
                SELECT publication_date
                FROM cache_log
                ORDER BY request_date DESC
            """, self.database)["publication_date"][0]
        # If we are this far then contact the API and cache the result
        self.log.info("Retrieving data for {call} from {api}.".format(
            api=self.name,
            call=self.slug,
        ))
        return self.request()

    def request(self):
        url = "".join([
            self.AWS_PRICING_API_BASE,
            self.uri,
        ])
        self.log.debug(url)
        r = timed(lambda:requests.get(url), log=self.log.info)()
        with io.BytesIO(r.content) as f:
            pub_date = pd.read_csv(io.BytesIO(f.read(1000).split(b"\n")[2]))
            f.seek(0)
            df = pd.read_csv(f, header=5)
        df.to_sql(self.slug, self.database, if_exists="replace")
        label, dt = pub_date
        pd.DataFrame(
            [[self.slug, dt, datetime.datetime.now()]],
            columns=["table", "publication_date", "request_date"]
        ).to_sql("cache_log", self.database, if_exists="append")
        return dt
