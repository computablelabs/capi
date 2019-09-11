import os
import hashlib
import boto3
from flask import request, g, current_app
from flask_restplus import Namespace, Resource
from core import constants as C
from core.celery import send_hash_after_mining
from core.protocol import is_registered
from apis.serializers import Listing, Listings
from apis.parsers import from_block_owner, parse_from_block_owner
from apis.helpers import listing_hash_join
from .serializers import NewListing
from .parsers import listing_parser
from .helpers import filter_listed
from core.dynamo import get_listings
from hexbytes import HexBytes

api = Namespace('Listings', description='Operations pertaining to the Computable Protocol Listing Object')

api.models['Listing'] = Listing
api.models['Listings'] = Listings
api.models['NewListing'] = NewListing

@api.route('/')
class ListingsRoute(Resource):
    @api.expect(from_block_owner)
    @api.marshal_with(Listings)
    def get(self):
        """
        Fetch and return all listings, optionally filtered from a given block number.
        """
        # TODO implement paging
        args = parse_from_block_owner(from_block_owner.parse_args())
        # protocol stuff... TODO handle blockchain reverts
        events = filter_listed(args['from_block'], args['filters'])
        # TODO any filtering for dynamo?
        everything = get_listings()
        it, tb = listing_hash_join(events, everything)

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
            for idx, item in enumerate(request.files.items()):
                # TODO contents = self.upload_to_s3...
                dest = os.path.join('/tmp/uploads/')

                if not os.path.exists(dest):
                    os.makedirs(dest)

                loc = f'{dest}{payload["listing_hash"]}'

                item[1].save(loc)
                self.upload_to_s3(payload['listing_hash'], loc)
                name = self.get_filename()
                payload['filename'] = name if name else item[0]

            # TODO use tx_hash to wait for mining so that we can call datatrust.set_data_hash
            # async -> g.w3.waitForTransactionReceipt... NOTE set timeout to ?
            keccak = self.get_keccak(loc)
            self.send_hash(
                payload['tx_hash'], 
                payload['listing_hash'], 
                HexBytes(keccak).hex() # convert to string for JSON serialization in Celery
            )
            # TODO what happens if it doesn't
            os.remove(loc)
        return {'message': C.NEW_LISTING_SUCCESS}, 201

    def send_hash(self, tx_hash, listing_hash, keccak):
        """
        Set the data hash after confirming listing has been mined
        NOTE: This is only here so that I can mock it for testing
        """
        send_hash_after_mining.delay(tx_hash, listing_hash, keccak)

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
        return None

    def upload_to_s3(self, listing_hash, location):
        """
        Upload file data to s3, keying it with the listing_hash
        """
        their_md5 = request.form.get('md5_sum')

        # Read the file the first time to verify the md5 of the uploaded file
        with open(location, 'rb') as data:
            contents = data.read()
            our_md5 = hashlib.md5(contents).hexdigest()
            if our_md5 != their_md5:
                print('MD5 check failed')
                api.abort(500, (C.SERVER_ERROR % 'file upload failed'))

        # Read the file a second time to upload to S3
        with open(location, 'rb') as data:
            res = g.s3.upload_fileobj(data, current_app.config['S3_DESTINATION'], listing_hash)

    def get_keccak(self, location):
        keccak_hash = None
        with open(location, 'rb') as data:
            b = data.read(1024*1024) # read file in 1MB chunks
            while b:
                keccak_hash = g.w3.keccak(b)
                b = data.read(1024*1024)
        return keccak_hash
