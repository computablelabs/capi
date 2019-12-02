"""
Boto3 CloudWatch client set in the global context for each request
Used to store CAPI performance metrics
"""
from datetime import datetime
from flask import current_app, g
import boto3

def set_cloudwatch(cloudwatch=None):
    """
    Place a boto3 cloudwatch client in the global env for this request
    """
    if 'cloudwatch' not in g:
        if cloudwatch == None:
            current_app.logger.info('setting Cloudwatch in the global env')
            cloudwatch = boto3.client('cloudwatch', region_name=current_app.config['REGION'])
        g.cloudwatch = cloudwatch

def set_metric(namespace):
    """
    Send any available metrics from the request to Cloudwatch
    """
    request_time = datetime.now()
    response_payload = []
    print(f'Metric namespace: {namespace}')
    for metric in g.metrics:
        for key in metric:
            print(f'Adding {key} with value {metric[key]}')
            response_payload.append(
                {
                    'MetricName': 'Response Time',
                    'Dimensions': [
                        {
                            'Name': namespace,
                            'Value': key
                        }
                    ],
                    'Value': metric[key],
                    'Unit': 'Milliseconds'
                }
            )
        if len(response_payload) > 0:
            response = g.cloudwatch.put_metric_data(
                Namespace=current_app.config['DNS_NAME'],
                MetricData=response_payload
            )