"""
Boto3 S3 client that lives in the global context for each request
NOTE: It is assumed that the bucket exists and bucket name is set in the current_app
config object at initialization (with tests handled via conftest)
"""
from flask import current_app, g
import boto3
from core.helpers import metrics_collector

@metrics_collector
def set_s3_client(s3=None):
    """
    Place a boto3 s3 client in the global env for this request
    NOTE: test env will pass a mocked s3 bucket via moto
    """
    if 's3' not in g:
        if s3 == None:
            current_app.logger.info('setting S3 in global env')
            s3 = boto3.client('s3', region_name=current_app.config['REGION'])
        g.s3 = s3

@metrics_collector
def get_listing_mimetype_and_size(hash):
    """
    Return the mimetype and filesize for a given listing
    """
    response = g.table.get_item(
        Key={
            'listing_hash': hash
        },
        ProjectionExpression='file_type, size'
    )
    if 'Item' in response:
        file_type = response['Item'].get('file_type', 'unknown')
        size = response['Item'].get('size', 0)
        return file_type, size
    else:
        return 'unknown', 0

@metrics_collector
def get_listing_and_meta(hash):
    """
    Fetch listing data from s3, write it to the temp storage location, and return its meta data
    """
    #TODO: add error handling around s3 retrieval
    download_location = f'{current_app.config["TMP_FILE_STORAGE"]}{hash}'
    s3_file = g.s3.download_file(
        current_app.config['S3_DESTINATION'],
        hash,
        download_location
    )
    mimetype, file_size = get_listing_mimetype_and_size(hash)

    return dict(
        listing_hash=hash,
        mimetype=mimetype,
        file_size=file_size
    )
