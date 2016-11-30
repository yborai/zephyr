import json

import pandas as pd
import requests
import sqlite3

from ..ddh import DDH

def compute_av(cache, compute_details):
    with open(cache, "r") as f:
        bit_response = json.load(f)
    bit_list = bit_response

    with open(compute_details, "r") as details_f:
        cc_response = json.load(details_f)
    # TODO: Reuse code from .compute_details to get this list.
    cc_response_instances = cc_response[0].get('Ec2Instances')
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

    con = sqlite3.connect(":memory:")
    ccdf.to_sql('cc', con, if_exists='replace')
    bddf.to_sql('bd', con, if_exists='replace')

    join = DDH.read_sql(
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

    return join
