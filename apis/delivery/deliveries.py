import os
from flask import current_app, g, send_file, after_this_request, make_response
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from core import constants as C
from core.helpers import get_gas_price_and_wait_time
from core.protocol import get_bytes_purchased
from .parsers import delivery_parser, parse_query
from .tasks import delivered_async
from .helpers import get_delivery, listing_accessed, was_delivered

api = Namespace('Delivery', description='Delivery endpoint for requesting purchased payloads')

# TODO i would argue that this route should be `/deliveries/hash?query='...'`
@api.route('/', methods=['GET'])
class DeliveryRoute(Resource):
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

        # in a past delivery situation there will be no delivery, but delivered event(s)
        past_purchase = was_delivered(delivery_hash, owner)

        current_app.logger.info(f'Retrieving {delivery_hash} for delivery')
        delivery_owner, requested_bytes, delivered_bytes = get_delivery(delivery_hash)

        # confirm that owner is past or current...
        if past_purchase or delivery_owner == owner:
            query_details = parse_query(args['query'])
            listing = query_details['listing_hash']
            listing_bytes = int(query_details['file_size'])
            mimetype = query_details['mimetype']
            title = query_details['title']

            # there are 3 situations that permit a download:

            #  1. the owner bought this in the past, past_purchase, from above

            #  2. a completed delivery exists but no past purchases (likely a download error)
            download_ready = False if past_purchase else delivered_bytes >= requested_bytes

            #  3. we are in a current purchase flow (not 1 or 2)
            bytes_purchased = 0 if (past_purchase or download_ready) else get_bytes_purchased(owner)
            current_purchase = False if (past_purchase or download_ready) else bytes_purchased >= listing_bytes

            if past_purchase or download_ready or current_purchase:

                # TODO: stream this from s3 rather than downloading then streaming
                tmp_file = f'{current_app.config["TMP_FILE_STORAGE"]}{listing}'

                # the current_purchase needs to perform protocol duties
                if current_purchase:
                    try:
                        price_and_time = get_gas_price_and_wait_time()
                    except Exception:
                        price_and_time = [C.MAINNET_GAS_DEFAULT, C.EVM_TIMEOUT]

                    # We have the file from S3, mark it as accessed and delivered
                    accessed_tx = listing_accessed(delivery_hash, listing, listing_bytes, price_and_time[0])
                    current_app.logger.info(f'{owner} used {listing_bytes} bytes accessing {listing}')
                    delivery_url = g.w3.keccak(
                        text=f"{current_app.config['DNS_NAME']}/deliveries/?delivery_hash={delivery_hash}")

                @after_this_request
                def remove_file(response):
                    try:
                        # first see if we can remove the tmp file
                        os.remove(tmp_file)
                        if current_purchase:
                            current_app.logger.info('Celery "delivered" task begun')
                            self.call_delivered(delivery_hash, delivery_url, accessed_tx, price_and_time)
                    except Exception as error:
                        current_app.logger.error(f'Error removing file or calling celery "delivered" task {error}')
                    return response

                current_app.logger.info('Requested delivery sent to user')
                response = make_response(
                    send_file(tmp_file, mimetype=mimetype, attachment_filename=listing, as_attachment=True)
                )
                file_extension = C.FILE_EXTENSIONS.get(mimetype, '')
                response.headers['Filename'] = f'{title}{file_extension}'
                return response
            else:
                current_app.logger.error(C.INSUFFICIENT_PURCHASED)
                api.abort(412, C.INSUFFICIENT_PURCHASED)
        else:
            current_app.logger.error(C.LOGIN_FAILED)
            api.abort(401, C.LOGIN_FAILED)

    def call_delivered(self, hash, url, tx, price_and_time):
        """
        abstracted method to call celery task. easy to mock this way
        """
        # stringify the args so celery can serialize them if needed
        hash_str = hash if isinstance(hash, str) else g.w3.toHex(hash)
        url_str = g.w3.toHex(url)  # we know it is not a str
        tx_str = tx if isinstance(tx, str) else g.w3.toHex(tx)  # should not be a str, but just in case
        price = price_and_time[0]
        duration = price_and_time[1]
        # NOTE do not store the results of delivered tasks
        delivered_async.s(hash_str, url_str, tx_str, price, duration).apply_async(ignore_result=True)
