from core.aws import get_secrets

DEVELOPMENT = True
DEBUG = True
PORT = 5000
HOST = '0.0.0.0'

PUBLIC_KEY = '0x9D330a81aA8c5311D33016Ab0A97787A0B28306e'

# CONTRACTS FOR FFA MARKET on skynet
ETHER_TOKEN_CONTRACT_ADDRESS = '0x306725200a6E0D504A7Cc9e2d4e63A492C72990d'
VOTING_CONTRACT_ADDRESS = '0x2B9a4a85791E66c5dc82Fb12f58Eb88ead6A167a'
PARAMETERIZER_CONTRACT_ADDRESS = '0xfB66e282708598Cef44b0A88Fa338af9350CAb87'
DATATRUST_CONTRACT_ADDRESS = '0xEF1Df5D48F08f25ADF297fF5dee5694b6C6599DE'
LISTING_CONTRACT_ADDRESS = '0x168f0DFe554f1aa614F87721C7e3d55c057c4F29'

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