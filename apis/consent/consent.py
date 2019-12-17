from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from core import constants as C
from apis.parsers import owner
from .parsers import consent_parser
from .serializers import Consent, NewConsent

api = Namespace('Consent', description='Enpoint for the POSTing end GETing of consent data')

api.models['Consent'] = Consent
api.models['NewConsent'] = Consent


@api.route('/', methods=['GET', 'POST'])
class ConsentRoute(Resource):
    @api.expect(owner)
    @api.response(200, C.SUCCESS)
    @api.marshal_with(Consent)
    def get(self):
        """
        Return the persisted consent data, if present, for the given public key
        """
        # TODO this

        return dict(timestamp=12345, from_us=True, version=1), 200

    @api.expect(consent_parser)
    @api.response(201, C.NEW_CONSENT_SUCCESS)
    @api.marshal_with(NewConsent)
    @jwt_required
    def post(self):
        """
        Given the json consent data for the JWT identified public_key, store it
        """
        consenter = get_jwt_identity()  # the key to store the json blob with

        # TODO this

        return dict(message=C.NEW_CONSENT_SUCCESS, consenter=consenter)
