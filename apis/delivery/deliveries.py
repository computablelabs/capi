import os
from flask import request, g, current_app, send_file, after_this_request
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required, decode_token, get_jwt_identity
from core import constants as C
from core.protocol import get_delivery, listing_accessed, delivered, get_bytes_purchased
from .parsers import delivery_parser, parse_query

api = Namespace('Delivery', description='Delivery endpoint for requesting purchased payloads')

# TODO i would argue that this route should be `/deliveries/hash?query='...'`
@api.route('/', methods=['GET'])
class Delivery(Resource):
    @api.expect(delivery_parser)
    @api.response(200, C.CONTENT_DELIVERED)
    @api.response(401, C.LOGIN_FAILED)
    @api.response(412, C.INSUFFICIENT_PURCHASED)
    @jwt_required
    def get(self):
        """
        Return the listing requested as a delivery object
        """
        args = delivery_parser.parse_args()
        delivery_hash = args['delivery_hash']
        owner = get_jwt_identity()
        current_app.logger.info(f'Retrieving {delivery_hash} for delivery')
        delivery_owner, requested_bytes, delivered_bytes = get_delivery(delivery_hash)
        if delivery_owner == owner:
            query_details = parse_query(args['query'])
            listing = query_details['listing_hash']
            listing_bytes = int(query_details['file_size'])
            mimetype = query_details['mimetype']

            bytes_purchased = get_bytes_purchased(owner)
            if bytes_purchased >= listing_bytes:
                tmp_file = f'{current_app.config["TMP_FILE_STORAGE"]}{listing}'

                # We have the file from S3, mark it as accessed and delivered
                accessed_tx = listing_accessed(delivery_hash, listing, listing_bytes)
                current_app.logger.info(f'{owner} used {listing_bytes} bytes accessing {listing}')
                delivery_url = g.w3.keccak(text=f"{current_app.config['DNS_NAME']}/deliveries/?delivery_hash={delivery_hash}")

                #TODO: stream this from s3 rather than downloading then streaming
                current_app.logger.info('Requested delivery sent to user')

                @after_this_request
                def remove_file(response):
                    try:
                        # first see if we can remove the tmp file
                        os.remove(tmp_file)
                        # before we can call delivered we must make sure the accessed tx has mined
                        accessed_rct = g.w3.eth.waitForTransactionReceipt(accessed_tx)
                        current_app.logger.info('listing_accessed transaction mined, calling for delivery completion')
                        # now see if we can get paid (not blocking here atm...)
                        delivered(delivery_hash, delivery_url)
                    except Exception as error:
                        current_app.logger.error(f'Error removing file or calling datatrust.delivered: {error}')
                    return response

                return send_file(tmp_file, mimetype=mimetype, attachment_filename=listing, as_attachment=True)
            else:
                current_app.logger.error(C.INSUFFICIENT_PURCHASED)
                api.abort(412, C.INSUFFICIENT_PURCHASED)
        else:
            current_app.logger.error(C.LOGIN_FAILED)
            api.abort(401, C.LOGIN_FAILED)
