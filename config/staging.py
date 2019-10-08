from core.aws import get_secrets

DEVELOPMENT = True
DEBUG = True
PORT = 5000
HOST = '0.0.0.0'

PUBLIC_KEY = '0x9D330a81aA8c5311D33016Ab0A97787A0B28306e'

# CONTRACTS FOR FFA MARKET on skynet
ETHER_TOKEN_CONTRACT_ADDRESS = '0xf3AB33fD326356e9aC525bfFc6865D42FdC237F0'
VOTING_CONTRACT_ADDRESS = '0x8109439D3A250f886379388CB6E29bBF64018255'
PARAMETERIZER_CONTRACT_ADDRESS = '0xa13811BfdD6B8D7d28efD954Cd604ECA876f91fD'
DATATRUST_CONTRACT_ADDRESS = '0xD9c1120FA4f001d10A6209210EF408733d07B392'
LISTING_CONTRACT_ADDRESS = '0xbEB3b451b589372d3b1A70d421B4B56EdDC0a654'

# AWS
secrets = get_secrets('staging', 'us-west-1')

TABLE_NAME = secrets['TABLE_NAME']
DB_URL = secrets['DB_URL']
S3_DESTINATION = secrets['S3_DESTINATION']
RPC_PATH = secrets['RPC_PATH']
PRIVATE_KEY = secrets['DATATRUST_KEY']
DNS_NAME = secrets['DNSName']
CELERY_BROKER_URL = secrets['CELERY_BROKER_URL']
CELERY_RESULT_BACKEND = secrets['CELERY_RESULT_BACKEND']
if 'LOG_LEVEL' in secrets:
    # Setting log leve in secrets allows changing log level without a code push
    LOG_LEVEL = secrets['LOG_LEVEL']
JWT_SECRET_KEY = secrets['JWT_SECRET_KEY']
