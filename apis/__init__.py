from flask_restplus import Api
from core import constants as C
from .listing.listings import api as listings
from .voting.candidates import api as candidates
from .health.status import api as status

api = Api(
    title=C.TITLE,
    version=C.VERSION,
    description=C.DESCRIPTION,
    )

api.add_namespace(listings, path='/listings')
api.add_namespace(candidates, path='/candidates')
api.add_namespace(status, path='/status')
