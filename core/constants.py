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
NEW_CONSENT_SUCCESS = 'Consent upload success'
MISSING_PAYLOAD_DATA = 'Incomplete payload in request body: %s'
SERVER_ERROR = 'Operation failed due to internal server error: %s'
LOGIN_SUCCESS = 'Signed message verified, access authorized'
LOGIN_FAILED = 'Signed message failed validation or access unauthorized'
CONTENT_DELIVERED = 'Requested content delivered'
INSUFFICIENT_PURCHASED = 'Insufficient bytes purchased for request'
PREVIEW_LISTING_TYPE_ONLY = 'Previews are only available for Listings or Applications'

# DB and API related messages
DB_SUCCESS = 'Database transaction completed successfully'
ITEM_NOT_FOUND = 'No results returned'
DB_ERROR = 'Operation failed due to database read/write error'
SERVER_ERROR = 'Operation failed due to internal server error'

# Protocol related messages
NOT_REGISTERED = 'This API is not currently the registered datatrust'
REGISTERED = 'This API is currently the registered datatrust'
REGISTERED_CANDIDATE = 'This API is an active candidate for datatrust'
RESOLVED = 'Candidate %s has been marked for resolution'
NEED_CMT_TO_STAKE = 'Insufficient CMT available to pay the stake for this operation.'
NEED_CMT_TO_PREVIEW = '''Preview requires that the requester have a CMT balance greater
than or equal to the current market stake'''
NOT_LISTED = 'Given listing hash is not a valid Listing'
NOT_A_CANDIDATE = 'Given hash is not a valid candidate'

# Celery related
CELERY_TASK_TIMEOUT = 5.0  # seconds, only applies to fetching task from redis
CELERY_TASK_FETCHED = 'Asynchronous task %s fetched successfully'
CELERY_TASK_CREATED = 'Asynchronous task %s created successfully'
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
EVM_TIMEOUT = 600  # seconds. how long to wait before bailing on things like `waitForTransactionReceipt`
POA_GAS_PRICE = 2  # Skynet is configured to take 2 Gwei, and rinkeby will as well
MAINNET_GAS_DEFAULT = 10  # kind of high gas price that should work in case of fetching it
TRANSACTION_TIMEOUT = 'Transaction mining time has exceeded the timeout of %s'
TRANSACTION_RETRY = 15  # seconds to sleep before checking for transaction receipt

# File extensions for known mimetypes
FILE_EXTENSIONS = {
    # application
    'application/applefile': '.applefile',
    'application/dicom': '.dicom',
    'application/ecmascript': '.js',
    'application/efi': '.efi',
    'application/geo+json': '.json',
    'application/gzip': '.gzip',
    'application/javascript': '.js',
    'application/json': '.json',
    'application/jwt': '.jwt',
    'application/mp21': '.mp21',
    'application/mp4': '.mp4',
    'application/mpeg4-generic': '.mp4',
    'application/octet-stream': '.bin',
    'application/ogg': '.ogg',
    'application/pdf': '.pdf',
    'application/pem-certificate-chain': '.pem',
    'application/pgp-encrypted': '.pgp',
    'application/pgp-signature': '.pgp',
    'application/pkcs10': '.pkcs10',
    'application/pkcs7-mime': '.pkcs7',
    'application/pkcs7-signature': '.pkcs7',
    'application/pkcs8': '.pkcs8',
    'application/pkcs8-encrypted': '.pkcs8',
    'application/pkcs12': '.pkcs12',
    'application/postscript': '.ps',
    'application/rfc+xml': '.xml',
    'application/rtf': '.rtf',
    'application/soap+xml': '.xml',
    'application/sql': '.sql',
    'application/text': '.txt',
    'application/vnd.adobe.flash.movie': '.flash',
    'application/vnd.apple.keynote': '.keynote',
    'application/vnd.apple.numbers': '.numbers',
    'application/vnd.apple.pages': '.pages',
    'application/vnd.coffeescript': '.coffee',
    'application/vnd.debian.binary-package': '.deb',
    'application/vnd.google-earth.kml+xml': '.kml',
    'application/vnd.google-earth.kmz': '.kmz',
    'application/vnd.ms-excel': '.xls',
    'application/vnd.ms-htmlhelp': '.chtml',
    'application/vnd.ms-powerpoint': '.ppt',
    'application/vnd.ms-word.document.macroEnabled.12': '.doc',
    'application/vnd.ms-word.template.macroEnabled.12': '.dot',
    'application/vnd.nintendo.snes.rom': '.rom',
    'application/vnd.nintendo.nitro.rom': '.rom',
    'application/vnd.rar': '.rar',
    'application/vnd.sqlite3': '.sqlite3',
    'application/vnd.tcpdump.pcap': '.pcap',
    'application/vnd.visio': '.vis',
    'application/xml': '.xml',
    'application/xml-dtd': '.xml',
    'application/zip': '.zip',

    # audio
    'audio/aac': '.aac',
    'audio/ac3': '.ac3',
    'audio/MPA': '.mpa',
    'audio/mp4': '.mp4',
    'audio/mpeg': '.mpeg',
    'audio/mpeg4-generic': '.mpeg',
    'audio/ogg': '.ogg',
    'audio/vnd.rip': '.rip',
    'audio/vorbis': '.vorbis',
    'audio/vorbis-config': '.vorbis',

    # font
    'font/otf': '.otf',
    'font/ttf': '.ttf',
    'font/woff': '.woff',
    'font/woff2': '.woff2',

    # image
    'image/bmp': '.bmp',
    'image/jpg': '.jpg',
    'image/jpeg': '.jpeg',
    'image/png': '.png',
    'image/tiff': '.tiff',

    # text
    'text/calendar': '.cal',
    'text/css': '.css',
    'text/csv': '.csv',
    'text/ecmascript': '.js',
    'text/html': '.html',
    'text/javascript': '.js',
    'text/markdown': '.md',
    'text/rtf': '.rtf',
    'text/sgml': '.sgml',
    'text/tab-separated-values': '.tsv',
    'text/vcard': '.vcard',
    'text/xml': '.xml',

    # video
    'video/H261': '.h261',
    'video/H263': '.h263',
    'video/H264': '.h264',
    'video/H265': '.h265',
    'video/JPEG': '.jpeg',
    'video/mp4': '.mp4',
    'video/mpeg4-generic': '.mpeg',
    'video/ogg': '.ogg',
    'video/quicktime': '.qt',
    'video/vc1': '.vc1',
    'video/vc2': '.vc2',
}
