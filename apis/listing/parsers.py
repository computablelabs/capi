from flask_restplus import reqparse
from werkzeug.datastructures import FileStorage

listing_parser = reqparse.RequestParser(bundle_errors=True)
listing_parser.add_argument('listing_hash', type=str, required=True, location='form', help='Unique identifier, as stored on-chain, for this listing')
listing_parser.add_argument('tx_hash', type=str, required=True, location='form', help='Transaction hash from client calling listing contract list method')
listing_parser.add_argument('file', type=FileStorage, location='files', required=False, help='Listing asset')
listing_parser.add_argument('title', type=str, required=True, location='form', help='Title of upload')
listing_parser.add_argument('description', type=str, required=True, location='form', help='Description of upload')
listing_parser.add_argument('owner', type=str, required=False, location='form', help='Owner of the upload')
listing_parser.add_argument('license', type=str, required=True, location='form', help='Usage license for upload')
listing_parser.add_argument('file_upload', type=FileStorage, required=True, location='files', help='Listing file asset')
listing_parser.add_argument('file_type', type=str, required=True, location='form', help='File type: image, video, audio, etc')
listing_parser.add_argument('md5_sum', type=str, required=True, location='form', help='MD5 of file asset')
listing_parser.add_argument('tags', type=str, required=False, location='form', action='split', help='Comma delimited list of tags for discovery')
