import os
from flask import request, g, current_app, send_file, after_this_request
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required, decode_token, get_jwt_identity
from core import constants as C
from core.protocol import get_voting, get_listing, has_stake
from core.s3 import get_listing_and_meta

api = Namespace('Previews', description='Endpoint which allows token holders to preview an asset')

@api.route('/<string:hash>', methods=['GET'])
class PreviewRoute(Resource):
    @api.response(200, C.CONTENT_DELIVERED)
    @api.response(400, C.PREVIEW_LISTING_TYPE_ONLY)
    @api.response(401, C.LOGIN_FAILED)
    @api.response(412, C.NEED_CMT_TO_PREVIEW)
    @jwt_required
    def get(self, hash):
        """
        Given an identifying hash (candidate, listing etc...), send a preview for the asset
        """
        address = get_jwt_identity()

        if not has_stake(address):
            current_app.logger.error(C.NEED_CMT_TO_PREVIEW)
            api.abort(412, C.NEED_CMT_TO_PREVIEW)
        else:
            # we only currently have preview for listing types
            voting = get_voting()
            is_application = voting.candidate_is(hash, C.candidate_kinds['application'])
            listing = get_listing()
            listed = listing.is_listed(hash)

            if is_application or listed:
                current_app.logger.info(f'Retrieving {hash} for preview')
                meta_data = get_listing_and_meta(hash)

                tmp_file = f'{current_app.config["TMP_FILE_STORAGE"]}{hash}'

                @after_this_request
                def remove_file(response):
                    try:
                        # first see if we can remove the tmp file
                        os.remove(tmp_file)
                    except Exception as error:
                        current_app.logger.error(f'Error removing file: {error}')
                    return response

                # TODO once the clients are ready, send previews back as in-line
                return send_file(tmp_file, mimetype=meta_data['mimetype'], attachment_filename=hash, as_attachment=True)
            else:
                current_app.logger.error(C.PREVIEW_LISTING_TYPE_ONLY)
                api.abort(400, C.PREVIEW_LISTING_TYPE_ONLY)
