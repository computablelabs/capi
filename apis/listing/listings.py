import os
import hashlib
import boto3
from flask import request, g, current_app
from flask_restplus import Namespace, Resource
from celery import uuid
from core import constants as C
from core.protocol import is_registered, get_single_listing
from core.dynamo import get_listing, get_listings
from apis.serializers import Listing, Listings
from apis.parsers import from_to_owner, parse_from_to_owner
from apis.helpers import extract_listing_hashes, listing_hash_join
from .serializers import NewListing
from .parsers import listing_parser
from .helpers import filter_listed, filter_listing_removed
from .tasks import send_data_hash_after_mining

api = Namespace('Listings', description='Operations pertaining to the Computable Protocol Listing Object')

api.models['Listing'] = Listing
api.models['Listings'] = Listings
api.models['NewListing'] = NewListing

# GET a single listing
@api.route('/<string:hash>', methods=['GET'])
class ListingRoute(Resource):
    @api.response(200, C.SUCCESS)
    @api.response(404, C.NOT_LISTED)
    @api.response(404, C.ITEM_NOT_FOUND)
    @api.marshal_with(Listing)
    def get(self, hash):
        """
        Given a listing hash, fetch it from protocol and dynamo, returning the data
        """
        # (owner, supply) from protocol
        owner_and_supply = get_single_listing(hash)
        if not owner_and_supply:
            current_app.logger.info(f'Listing {hash} could not be found on chain')
            api.abort(404, C.NOT_LISTED)
        # fetch the dynamo data
        meta = get_listing(hash)
        # dynamo wraps the returned payload in 'Item'...
        listing = meta['Item']
        if not listing:
            current_app.logger.info(f'Listing {hash} could not be found in db')
            api.abort(404, C.ITEM_NOT_FOUND)

        # just append the supply as owner is already there
        listing.update({'supply': owner_and_supply[1]})
        return dict(listing), 200

# GET multiple listings or POST a listing
@api.route('/')
class ListingsRoute(Resource):
    @api.expect(from_to_owner)
    @api.marshal_with(Listings)
    @api.response(200, C.SUCCESS)
    def get(self):
        """
        Fetch and return all listings, optionally filtered from a given block number.
        """
        args = parse_from_to_owner(from_to_owner.parse_args())
        # protocol stuff... TODO handle blockchain reverts
        current_app.logger.info(f'Fetching listings from block {args["from_block"]} to block {args["to_block"]}')
        # use this list to filter by so that we only return live listings
        removed = filter_listing_removed(args['from_block'], args['to_block'])
        # we need the hashes themselves to pass as a filter_by to ...join
        removed_hashes = extract_listing_hashes(removed) # not using the to_block on removed

        listed = filter_listed(args['from_block'], args['to_block'], args['filters'])
        # TODO any filtering for dynamo?
        all_the_dynamo = get_listings()
        current_app.logger.debug('retrieved listings from db')
        # filter out any removed by passing them
        it, tb = listing_hash_join(listed, all_the_dynamo, removed_hashes)

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
            current_app.logger.error('POST new listing called but this server is not the datatrust')
            api.abort(500, C.NOT_REGISTERED) # TODO different error code?
        else:
            payload = self.get_payload()
            file_item = request.files.items()
            for idx, item in enumerate(file_item):
                # TODO contents = self.upload_to_s3...
                dest = os.path.join('/tmp/uploads/')

                if not os.path.exists(dest):
                    os.makedirs(dest)

                loc = f'{dest}{payload["listing_hash"]}'

                item[1].save(loc)
                self.upload_to_s3(payload['listing_hash'], loc)
                current_app.logger.info(f'Listing hash {payload["listing_hash"]} uploaded to S3')
                name = self.get_filename()
                payload['filename'] = name if name else item[0]

            file_info = os.stat(loc)
            payload['size'] = file_info.st_size
            db_write = self.save_to_db(payload)
            current_app.logger.info(f'Listing hash {payload["listing_hash"]} saved to db')

            keccak = self.get_keccak(loc)

            uid = self.send_data_hash(
                payload['tx_hash'],
                payload['listing_hash'],
                g.w3.toHex(keccak)) # convert to string for JSON serialization in Celery

            current_app.logger.info(f'Listing hash {payload["listing_hash"]} data hash sent to protocol')

            # TODO what happens if it doesn't
            os.remove(loc)

            current_app.logger.info(C.NEW_LISTING_SUCCESS)

            return dict(message=C.NEW_LISTING_SUCCESS, task_id=uid), 201

    def send_data_hash(self, tx_hash, listing, data_hash):
        uid = uuid()
        send_data_hash_after_mining.s(tx_hash,listing,data_hash).apply_async(task_id=uid)

        return uid

    def get_payload(self):
        """
        """
        payload = {}
        for item in ['tx_hash', 'listing_hash', 'title', 'description', 'license', 'file_type', 'md5_sum', 'owner']:
            val = request.form.get(item)
            if not val:
                current_app.logger.warning(C.MISSING_PAYLOAD_DATA % item)
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
                current_app.logger.warning(C.SERVER_ERROR % 'file upload failed, incorrect md5')
                api.abort(400, (C.SERVER_ERROR % 'file upload failed, incorrect md5'))

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

    def save_to_db(self, payload):
        response = g.table.put_item(
            Item=payload
        )
        return response
