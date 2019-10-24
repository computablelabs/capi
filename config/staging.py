from core.aws import get_secrets

DEVELOPMENT = True
DEBUG = True
PORT = 5000
HOST = '0.0.0.0'

PUBLIC_KEY = '0x9D330a81aA8c5311D33016Ab0A97787A0B28306e'

# CONTRACTS FOR FFA MARKET on skynet
ETHER_TOKEN_CONTRACT_ADDRESS = '0x6Ab1e58FDe8D70E68463722cc426Ebb5332ee5Aa'
MARKET_TOKEN_CONTRACT_ADDRESS = '0x993Ee9B19e760ae7651B89C68066D656Ac81246F'
VOTING_CONTRACT_ADDRESS = '0xE778070E092798092E2a3a4E5E1e53174BD4e917'
PARAMETERIZER_CONTRACT_ADDRESS = '0xdAfb952371C2EFD506B920E56834ea9Fd102Ce0C'
RESERVE_CONTRACT_ADDRESS = '0xBB9e1f4D71A2d5B19D65757B452005A1a02186BC'
DATATRUST_CONTRACT_ADDRESS = '0xA451e91bdB58e1B52707B41f2af2c1774221eD0C'
LISTING_CONTRACT_ADDRESS = '0xD5df48Da838676E246e9537bB298E19B0aa00c58'

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
