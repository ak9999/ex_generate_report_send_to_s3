from io import StringIO
from csv import DictWriter
from datetime import datetime
import json
import os

import ninjarmmpy
import boto3


def return_servers_report(key: str, secret: str) -> str:
    """Returns a report of devices without anti-virus in CSV format.
    Keyword arguments:
    key:    str     -- NinjaRMM API Key ID
    secret: str     -- NinjaRMM API Secret ID
    """
    client = ninjarmmpy.Client(
        AccessKeyID=key,
        SecretAccessKey=secret
    )
    device_ids = client.getGroupDeviceIds(id=os.getenv(key='DEVICE_GROUP'))
    devices = [client.getDevice(id=i) for i in device_ids]
    output = []
    with StringIO() as f:
        fields = [
            'organization', 'dns_name', 'role', 'device_id', 'os_name',
            'needs_reboot', 'last_user', 'device_link'
        ]
        writer = DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for d in devices:
            device_role = d['nodeClass']
            device_name = d['dnsName']
            device_org = client.getOrganization(id=d['organizationId'])['name']
            row = {
                'organization': device_org,
                'dns_name': device_name,
                'role': device_role,
                'device_id': d.get('id', None),
                'os_name': d.get('os', None).get('name', None),
                'needs_reboot': d.get('os', None).get('needsReboot', None),
                'last_user': d.get('lastLoggedInUser', None),
                'device_link': f"https://app.ninjarmm.com/#/deviceDashboard/{d.get('id', 'Error')}/overview"
            }
            output.append(row)
        writer.writerows(output)
        return f.getvalue()


def lambda_handler(event, context):
    key, secret, bucket = (
        os.getenv(key='NRMM_KEY_ID'),
        os.getenv(key='NRMM_SECRET'),
        os.getenv(key='S3_BUCKET')
    )
    if not all((key, secret, bucket)):
        exit(code=-3)
    servers = return_servers_report(key, secret)
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(
        Key=f'{datetime.today()}.csv',
        Body=servers
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Mission complete!')
    }
