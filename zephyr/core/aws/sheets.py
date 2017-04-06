import pandas as pd
import sqlite3

from .calls import AWSEC2Pricing
from ..ddh import DDH
from ..sheet import Sheet
from ..cc.calls import ComputeDetails


class AWSEC2PricingSheet(Sheet):
    name = "ec2-pricing"
    title = "AWS EC2 Pricing"
    calls = (ComputeDetails, AWSEC2Pricing)

    def load_data(self):
        CD, EC2P = self.clients
        response = CD.cache_policy(
            self.account, self.date, self.expire_cache
        )
        CD.parse(response)
        ddh = CD.to_ddh()
        client_data = [bool(ddh) and bool(ddh.data)]
        cd_df = pd.DataFrame(ddh.data, columns=ddh.header)
        cd_df.to_sql(CD.slug, self.con, if_exists='replace')
        types = list(pd.read_sql(
            """select distinct("InstanceType") from "{}" """.format(CD.slug),
            self.con
        )["InstanceType"].values)
        pd.read_sql(
            """select * from "{table}" where "Instance Type" in ('{types}')""".format(
                table=EC2P.slug,
                types="', '".join(types),
            ),
            self.database
        ).to_sql(EC2P.slug, self.con, if_exists='replace')
        cd_key = """(''
                || SUBSTR(cd."Region", 0, INSTR(cd."Region", " ("))
                || cd."Tenancy"
                || cd."InstanceType"
        )"""

        ep_key = """(''
                || SUBSTR(ep."Location", 0, INSTR("Location", " ("))
                || ep."Tenancy"
                || ep."Instance Type"
        )"""
        df = pd.read_sql("""
            SELECT
                cd."InstanceId",
                cd."Region",
                cd."Tenancy",
                cd."InstanceType",
                cd."PricingPlatform",
                cd."LaunchTime",
                MIN(ep."PricePerUnit")*24*30 AS "Min",
                MAX(ep."PricePerUnit")*24*30 AS "Max",
                count(*)
            FROM
                "compute-details" AS cd LEFT OUTER JOIN
                "ec2-pricing" AS ep ON ({cpk}={epk})
            WHERE 1
                AND {epk} IS NOT NULL
                AND ep."TermType" = 'OnDemand'
            GROUP BY "InstanceId"
            ORDER BY MIN(ep."PricePerUnit")*24*30 DESC
        """.format(
            cpk=cd_key,
            epk=ep_key,
        ), self.con)

        header = df.columns
        cu_data = [[
            self.clean.get(index, lambda x:x)(row[index])
            for index in range(len(header))
        ] for row in df.values]
        cu_ddh = DDH(data=cu_data, header=list(header))
        self._ddh = cu_ddh
        return self._ddh

    def to_ddh(self):
        if(self._ddh):
            return self._ddh

    def to_xlsx(self, book, **kwargs):
        """Format the AWS EC2 Pricing sheet."""
        # Load the data.
        if not self.ddh:
            return

        self.book = book

        # Insert raw data.
        self.sheet = book.add_worksheet(self.title)
        self.get_formatting()
        self.put_label(self.title)
        self.put_table(top=1)

        return self.sheet
