"""
Boto3 S3 client that lives in the global context for each request
NOTE: It is assumed that the bucket exists and bucket name is set in the current_app
config object at initialization (with tests handled via conftest)
"""
from flask import current_app, g
import boto3

def set_s3_client(s3=None):
    """
    Place a boto3 s3 client in the global env for this request
    NOTE: test env will pass a mocked s3 bucket via moto
    """
    if 's3' not in g:
        if s3 == None:
            s3 = boto3.client('s3', region_name=current_app.config['REGION'])
        g.s3 = s3
