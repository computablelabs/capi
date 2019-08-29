import os
import hashlib
import boto3
from flask import request, g
from flask_restplus import Namespace, Resource
from core import constants as C
from core.protocol import is_registered
from .parsers import listing_parser, listings_parser, parse_listings
from .serializers import Listing, Listings, NewListing
from .helpers import filter_listed

api = Namespace('Listings', description='Operations pertaining to the Computable Protocol Listing Object')

api.models['Listing'] = Listing
api.models['Listings'] = Listings
api.models['NewListing'] = NewListing

@api.route('/')
class ListingsRoute(Resource):
    @api.expect(listings_parser)
    @api.marshal_with(Listings)
    def get(self):
        """
        Fetch and return all listings, optionally filtered from a given block number.
        """
        # TODO implement paging

        args = parse_listings(listings_parser.parse_args())

        # protocol stuff... TODO handle blockchain reverts
        events = filter_listed(args['from_block'], args['filters'])
        hashes = []
        tb = 0

        for event in events:
            hashes.append(g.w3.toHex(event['args']['hash'])) # byte array not json serializable, convert it
            tb = max(to_block, event['blockNumber'])

        # TODO now fetch dynamo items with the hashes
        it = []

        return dict(items=it, from_block=args['from_block'], to_block=tb), 200

    @api.expect(listing_parser)
    @api.response(201, C.NEW_LISTING_SUCCESS)
    @api.response(400, C.MISSING_PAYLOAD_DATA)
    @api.response(500, C.SERVER_ERROR)
    @api.marshal_with(NewListing)
    def post(self):
        """
        Submit a new listing to the Datatrust API.
        NOTE: ATM this method is 'setup' for a single file upload.
        TODO: Adjust if multiple files are allowed
        """

        # as it stands we cant have a before_request at the api level. it is however slated as a resplus enhancement
        # github.com/noirbizarre/flask-restplus/issues/140
        # TODO switch to that over checking this in every `setter` when it's available
        if is_registered() == False:
            api.abort(500, C.NOT_REGISTERED) # TODO different error code?
        else:
            payload = self.get_payload()
            file_item = request.files.items()
            self.upload_to_s3(file_item[1], payload['listing_hash'])
            name = self.get_filename()
            payload['filename'] = name if name else file_item[0]

    def get_payload(self):
        """
        """
        payload = {}
        for item in ['tx_hash', 'listing_hash', 'title', 'license', 'file_type', 'md5_sum']:
            val = request.form.get(item)
            if not val:
                api.abort(400, (C.MISSING_PAYLOAD_DATA % item))
            else:
                payload[item] = val

        tags = request.form.get('tags')
        if tags:
            payload['tags'] = [tag.strip() for tag in tags.split(',')]

        return payload

    def get_filename(self):
        """
        In case the original filenames is useful, persist it with the upload metadata
        """
        names = request.form.get('filenames')
        if names:
            filenames = names.split(',')

        return filenames[0] if filenames[0] else None

    def upload_to_s3(self, item, listing_hash):
        """
        Upload file data to s3, keying it with the listing_hash
        """
        their_md5 = request.form.get('md5_sum')
        dest = os.path.join('/tmp/uploads/')

        if not os.path.exists(dest):
            os.makedirs(dest)

        loc = f'{dest}{listing_hash}'

        item.save(loc)

        with open(loc, 'rb') as data:
            contents = data.read()
            our_md5 = hashlib.md5(contents).hexdigest()
            if our_md5 != their_md5:
                api.abort(500, (C.SERVER_ERROR % 'file upload failed'))

            s3 = boto3.client('s3')
            s3.upload_fileobj(data, current_app.config['S3_DESTINATION'], listing_hash)
