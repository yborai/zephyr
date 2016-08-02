import requests
import json
import base64
import pandas as pd
import sqlite3
from requests.auth import HTTPBasicAuth

from .common import DDH, timed, ToolkitDataController
from .core import Warp

from cement.core import controller

class ToolkitComputeAV(ToolkitDataController):
    class Meta:
        label = "compute-av"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the AV of instance meta information"

        arguments = ToolkitDataController.Meta.arguments #+ [(
        #    ["--cc_api_key"], dict(
        #        type=str,
        #        help="The CloudCheckr API key to use."
        #    )
        #)]

    @controller.expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        con = sqlite3.connect(":memory:")
        cache = self.app.pargs.cache
        compute_details = self.app.pargs.compute_details
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        if(not compute_details):
            raise NotImplementedError 
        self.app.log.info("Using compute_details response: {compute_details}".format(compute_details=compute_details))
        with open(cache, "r") as f:
            bit_response = json.load(f)
        bit_list = bit_response
        
        with open(compute_details, "r") as details_f:
            cc_response = json.load(details_f)
        cc_response_instances = cc_response.get('Ec2Instances')
        list_of_instances = []
        for instance in cc_response_instances:
            cc_instance_dict = {
            'Name': instance['InstanceName'],
            'Instance ID': instance['InstanceId'],
            'Instance Type': instance['InstanceType'],
            'Public IP(s)': instance['PublicIpAddress'],
            'Private IP(s)': instance['PrivateIpAddress']}
            list_of_instances.append(cc_instance_dict)
        cc_list = list_of_instances

        ccdf = pd.DataFrame(cc_list)
        bddf = pd.DataFrame(bit_list)
        ccdf.to_sql('cc', con, if_exists='replace')
        bddf.to_sql('bd', con, if_exists='replace')

        jodf = pd.read_sql(
            " SELECT"
            "     CASE"
            "         WHEN bd.'Product Outdated' = 0 THEN 'Present'"
            "         WHEN bd.'Product Outdated' = 1 THEN 'Outdated'"
            "         ELSE 'Absent'"
            "     END as 'AV Status',"
            "     cc.Name, cc.'Instance ID', cc.'Instance Type',"
            "     cc.'Public IP(s)', cc.'Private IP(s)'"
            " FROM cc LEFT OUTER JOIN bd ON bd.Name=cc.Name"
            " ORDER BY bd.'Product Outdated' DESC, cc.Name",
            con
        )

        headers = list(jodf.columns)
        data = [list(row) for row in jodf.values]

        out = DDH(headers=headers, data=data)
        self.app.render(out)
        return out
