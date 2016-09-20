import json
import boto3

from .common import DDH

def domains(access_key_id, secret_key, session_token):
    route53 = boto3.client(
        "route53",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token
    )

    zones = route53.list_hosted_zones()
    domains_list = zones["HostedZones"]
    data = []
    header = ["Name", "Id", "ResourceRecordSetCount", "CallerReference"]
    for domain in domains_list:
        data.append([
            domain["Name"],
            domain["Id"],
            domain["ResourceRecordSetCount"],
            domain["CallerReference"],
            ])

    return DDH(header=header, data=data)
