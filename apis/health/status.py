from flask_restplus import Namespace, Resource
from core.protocol import is_registered, get_backend_url

api = Namespace('Status', description='Operations pertaining to the health and status of the API')

@api.route('/', methods=['GET'])
class StatusRoute(Resource):
    def get(self):
        """
        """
        r = is_registered()
        u = get_backend_url()

        # TODO marshalling
        return {'registered': r, 'url': u}, 200
