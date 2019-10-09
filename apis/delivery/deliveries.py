from flask import request, g, current_app, send_file
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required, decode_token, get_jwt_identity
from core import constants as C
from core.protocol import get_delivery, listing_accessed, delivered
from .parsers import delivery_parser

api = Namespace('Delivery', description='Delivery endpoint for requesting purchased payloads')

@api.route('/<string:delivery_hash>', methods=['GET'])
class Delivery(Resource):
    @api.expect(delivery_parser)
    @api.response(200, C.CONTENT_DELIVERED)
    @api.response(401, C.LOGIN_FAILED)
    @api.response(412, C.INSUFFICIENT_PURCHASED)
    @jwt_required
    def get(self, delivery_hash):
        """
        Return the listing requested as a delivery object
        """
        args = delivery_parser.parse_args()
        owner = get_jwt_identity()
        current_app.logger.info(f'Retrieving {delivery_hash} for delivery')
        authorized_delivery = [delivery_hash, 14, 0]
        # delivery_owner = authorized_delivery[0]
        delivery_owner = owner # temp workaround until I figure out request_delivery
        listing = args['listing_hash']
        if delivery_owner == owner:
            bytes_purchased = authorized_delivery[1]
            listing_bytes = self.listing_bytes(listing)
            if bytes_purchased >= listing_bytes:
                tmp_file = f'/tmp/{delivery_hash}'
                #TODO: add error handling around s3 retrieval
                s3_file = g.s3.download_file(
                    current_app.config['S3_DESTINATION'],
                    listing,
                    tmp_file
                )
                # We have the file from S3, mark it as accessed and delivered
                listing_accessed(delivery_hash, listing, listing_bytes)
                delivery_url = g.w3.keccak(text=f"{current_app.config['DNS_NAME']}/deliveries/{delivery_hash}")
                delivered(delivery_hash, delivery_url)
                mimetype = self.get_mimetype(listing)
                #TODO: stream this from s3 rather than downloading then streaming
                current_app.logger.info('Requested delivery sent to user')
                return send_file(tmp_file, mimetype=mimetype, attachment_filename=id)
            else:
                current_app.logger.error(C.INSUFFICIENT_PURCHASED)
                api.abort(412, C.INSUFFICIENT_PURCHASED)
        else:
            current_app.logger.error(C.LOGIN_FAILED)
            api.abort(401, C.LOGIN_FAILED)

    def listing_bytes(self, key):
        """
        Return the size of an object stored in s3
        """
        s3_object = g.s3.head_object(
            Bucket=current_app.config['S3_DESTINATION'],
            Key=key
        )
        if 'ContentLength' in s3_object:
            return s3_object['ContentLength']
        else:
            return None

    def get_mimetype(self, key):
        """
        Return the mimetype for the listing
        """
        response = g.table.get_item(
            Key={
                'listing_hash': key
            },
            ProjectionExpression='file_type'
        )
        if 'Item' in response:
            return response['Item'].get('file_type', 'unknown')
        else:
            return 'unknown'
