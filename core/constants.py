TITLE = 'Computable API'
VERSION = '3'
DESCRIPTION = 'API as Datatrust template for the Computable Protocol'
UNHANDLED_EXCEPTION = 'An unhandled exception occurred'

# Voting Contract Candidate Kinds
candidate_kinds = {
    'application': 1,
    'challenge': 2,
    'reparam': 3,
    'registration': 4,
    }

# Verb Messages
NEW_LISTING_SUCCESS = 'Listing upload success. Data hash sent to protocol'
MISSING_PAYLOAD_DATA = 'Incomplete payload in request body: %s'
SERVER_ERROR = 'Operation failed due to internal server error: %s'
LOGIN_SUCCESS = 'Signed message verified, access authorized'
LOGIN_FAILED = 'Signed message failed validation or access unauthorized'
CONTENT_DELIVERED = 'Requested content delivered'
INSUFFICIENT_PURCHASED = 'Insufficient bytes purchased for request'
PREVIEW_LISTING_TYPE_ONLY = 'Previews are only available for Listings or Applications'

# DB related messages
DB_SUCCESS = 'Database transaction completed successfully'
ITEM_NOT_FOUND = 'No results returned'
DB_ERROR = 'Operation failed due to database read/write error'

# Protocol related messages
NOT_REGISTERED = 'This API is not currently the registered datatrust'
REGISTERED = 'This API is currently the registered datatrust'
REGISTERED_CANDIDATE = 'This API is an active candidate for datatrust'
RESOLVED = 'Candidate %s has been marked for resolution'
NEED_CMT_TO_STAKE = 'Insufficient CMT available to pay the stake for this operation.'
NEED_CMT_TO_PREVIEW = 'Preview requires that the requester have a CMT balance greater than or equal to the current market stake'

# Celery related
CELERY_TASK_TIMEOUT = 5.0 # seconds
CELERY_TASK_FETCHED = 'Asynchronous task %s fetched successfully'
CELERY_TASK_CREATED= 'Asynchronous task %s created successfully'
CELERY_TASK_NOT_FOUND = 'Asynchronous task %s not found'
CELERY_TASK_TIMED_OUT = 'Asynchronous task %s timed out'
STARTED = 'STARTED'
PENDING = 'PENDING'
SUCCESS = 'SUCCESS'
FAILURE = 'FAILURE'
WAITING_FOR_RECEIPT = 'Waiting on transaction receipt for %s'
TRANSACTION_MINED = 'Transaction mined: %s'
WAITING_FOR_NAMED_RECEIPT = 'Waiting on %s transaction receipt for %s'
NAMED_TRANSACTION_MINED = '%s transaction mined: %s'

# EVM related (also celery task)
EVM_TIMEOUT = 600 # seconds. how long to wait before bailing on things like `waitForTransactionReceipt`
POA_GAS_PRICE = 2 # Skynet is configured to take 2 Gwei, and rinkeby will as well
MAINNET_GAS_DEFAULT = 10 # kind of high gas price that should work in case of fetching it
