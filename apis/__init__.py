from flask_restplus import Api
from core import constants as C
from .listing.listings import api as listings
from .voting.candidates import api as candidates
from .task.tasks import api as tasks
from .health.status import api as status
from .authorize.login import api as authorize
from .delivery.deliveries import api as deliveries
from .preview.previews import api as previews
from .consent.consent import api as consent

api = Api(
    title=C.TITLE,
    version=C.VERSION,
    description=C.DESCRIPTION,
    )

api.add_namespace(listings, path='/listings')
api.add_namespace(candidates, path='/candidates')
api.add_namespace(tasks, path='/tasks')
api.add_namespace(status, path='/status')
api.add_namespace(authorize, path='/authorize')
api.add_namespace(deliveries, path='/deliveries')
api.add_namespace(previews, path='/previews')
api.add_namespace(consent, path='/consent')
