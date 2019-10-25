from flask import current_app, g
from flask_restplus import reqparse

delivery_parser = reqparse.RequestParser(bundle_errors=True)
delivery_parser.add_argument('delivery_hash', type=str, required=True, location='args', help='The delivery hash for the request to fulfill')
delivery_parser.add_argument('query', type=str, required=True, location='args', help='The query to execute for this delivery')

def parse_query(query):
    """
    Execute the query for the delivery and return the payload for the client
    """
    #TODO: add error handling around s3 retrieval
    download_location = f'{current_app.config["TMP_FILE_STORAGE"]}{query}'
    s3_file = g.s3.download_file(
        current_app.config['S3_DESTINATION'],
        query,
        download_location
    )
    mimetype, file_size = get_mimetype_and_size(query)

    return dict(
        listing_hash=query,
        mimetype=mimetype,
        file_size=file_size
    )

def get_mimetype_and_size(key):
    """
    Return the mimetype for the listing
    """
    response = g.table.get_item(
        Key={
            'listing_hash': key
        },
        ProjectionExpression='file_type, size'
    )
    if 'Item' in response:
        file_type = response['Item'].get('file_type', 'unknown')
        size = response['Item'].get('size', 0)
        return file_type, size
    else:
        return 'unknown', 0
