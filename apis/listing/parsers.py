from flask_restplus import reqparse
from werkzeug.datastructures import FileStorage

listings_parser = reqparse.RequestParser()
listings_parser.add_argument('from-block', type=int, location='args', help='Block number to begin scanning from')
listings_parser.add_argument('owner', location='args', help='Ethereum account which owns this listing')

listing_parser = reqparse.RequestParser(bundle_errors=True)
listing_parser.add_argument('file', type=FileStorage, location='files', required=False, help='Listing asset')
listing_parser.add_argument('tx_hash', type=str, required=True, location='form', help='Transaction hash from client calling listing contract list method')
listing_parser.add_argument('title', type=str, required=True, location='form', help='Title of upload')
listing_parser.add_argument('description', type=str, required=True, location='form', help='Description of upload')
listing_parser.add_argument('owner', type=str, required=False, location='form', help='Owner of the upload')
listing_parser.add_argument('license', type=str, required=True, location='form', help='Usage license for upload')
listing_parser.add_argument('file_upload', type=FileStorage, required=True, location='files', help='Listing file asset')
listing_parser.add_argument('file_type', type=str, required=True, location='form', help='File type: image, video, audio, etc')
listing_parser.add_argument('md5_sum', type=str, required=True, location='form', help='MD5 of file asset')
listing_parser.add_argument('tags', type=str, required=False, location='form', action='split', help='Comma delimited list of tags for discovery')

def parse_listings(args):
    """
    return a dict of the input items required by the '/' GET route
    """
    b = args['from-block'] if args['from-block'] != None else 0
    f = {'owner': args['owner']} if args['owner'] != None else None

    return dict(from_block=b, filters=f)
