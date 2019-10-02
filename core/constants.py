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

# DB related messages
DB_SUCCESS = 'Database transaction completed successfully'
ITEM_NOT_FOUND = 'No results returned'
DB_ERROR = 'Operation failed due to database read/write error'

# Protocol related messages
NOT_REGISTERED = 'This API is not currently the registered datatrust'
REGISTERED = 'This API is currently the registered datatrust'
REGISTERED_CANDIDATE = 'This API is an active candidate for datatrust'
RESOLVED = 'Candidate %s has been marked for resolution'

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
EVM_TIMEOUT = 300 # seconds. how long to wait before bailing on things like `waitForTransactionReceipt`
