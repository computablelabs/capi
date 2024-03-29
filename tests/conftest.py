import os
import json
from flask import current_app
import pytest
import boto3
from moto import mock_dynamodb2, mock_s3, mock_cloudwatch
from app import celery as c
from app.factory import create_app
from web3 import Web3
from eth_keys import keys
from core.protocol import set_w3
from core.dynamo import set_dynamo_table
from core.s3 import set_s3_client
from core.cloudwatch import set_cloudwatch
import computable # we use this to get the path to the contract abi/bin in the installed lib (rather than copy/paste them)
from computable.contracts import EtherToken
from computable.contracts import MarketToken
from computable.contracts import Voting
from computable.contracts import Parameterizer
from computable.contracts import Reserve
from computable.contracts import Datatrust
from computable.contracts import Listing
from computable.helpers.transaction import transact

@pytest.fixture(scope='module')
def test_provider():
    return Web3.EthereumTesterProvider()

@pytest.fixture(scope='module')
def w3(test_provider):
    instance = Web3(test_provider)
    instance.eth.defaultAccount = instance.eth.accounts[0]
    return instance

# on occassion we may need a user with a private key to test
@pytest.fixture(scope='module')
def passphrase():
    return 'im.a.lumberjack'

@pytest.fixture(scope='module')
def pk():
    return keys.PrivateKey(b'\x01' * 32)

@pytest.fixture(scope='module')
def user(w3, pk, passphrase):
    return w3.geth.personal.importRawKey(pk.to_hex(), passphrase)

@pytest.fixture(scope='module')
def ether_token(w3):
    # this might be kind of a hack - but its a damn cool one
    contract_path = os.path.join(computable.__path__[0], 'contracts')
    with open(os.path.join(contract_path, 'ethertoken', 'ethertoken.abi')) as f:
        abi = json.loads(f.read())
    with open(os.path.join(contract_path, 'ethertoken', 'ethertoken.bin')) as f:
        bc = f.read()
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    # TODO this must change on computable.py next update
    tx_hash = deployed.constructor().transact()
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    instance = EtherToken(w3.eth.defaultAccount)
    instance.at(w3, tx_rcpt['contractAddress'])
    return instance

@pytest.fixture(scope='module')
def market_token_opts():
    return {'init_bal': Web3.toWei(4, 'ether')}

@pytest.fixture(scope='module')
def market_token_pre(w3, market_token_opts):
    """
    *_pre instances are before privileged are set...
    """
    contract_path = os.path.join(computable.__path__[0], 'contracts')
    with open(os.path.join(contract_path, 'markettoken', 'markettoken.abi')) as f:
        abi = json.loads(f.read())
    with open(os.path.join(contract_path, 'markettoken', 'markettoken.bin')) as f:
        bc = f.read()
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    tx_hash = deployed.constructor(w3.eth.defaultAccount,
        market_token_opts['init_bal']).transact()
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    instance = MarketToken(w3.eth.defaultAccount)
    instance.at(w3, tx_rcpt['contractAddress'])
    return instance

@pytest.fixture(scope='module')
def voting_pre(w3, market_token_pre):
    contract_path = os.path.join(computable.__path__[0], 'contracts')
    with open(os.path.join(contract_path, 'voting', 'voting.abi')) as f:
        abi = json.loads(f.read())
    with open(os.path.join(contract_path, 'voting', 'voting.bin')) as f:
        bc = f.read()
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    tx_hash = deployed.constructor(market_token_pre.address).transact()
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    instance = Voting(w3.eth.defaultAccount)
    instance.at(w3, tx_rcpt['contractAddress'])
    return instance

@pytest.fixture(scope='module')
def parameterizer_opts(w3):
    return {
                'price_floor': w3.toWei(1, 'szabo'),
                'spread': 110,
                'list_reward': w3.toWei(250, 'szabo'),
                'stake': w3.toWei(1, 'finney'),
                'vote_by': 100,
                'plurality': 50,
                'backend_payment': 25,
                'maker_payment': 25,
                'cost_per_byte': w3.toWei(100, 'gwei')
            }

@pytest.fixture(scope='module')
def parameterizer(w3, market_token_pre, voting_pre, parameterizer_opts):
    contract_path = os.path.join(computable.__path__[0], 'contracts')
    with open(os.path.join(contract_path, 'parameterizer', 'parameterizer.abi')) as f:
        abi = json.loads(f.read())
    with open(os.path.join(contract_path, 'parameterizer', 'parameterizer.bin')) as f:
        bc = f.read()
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    tx_hash = deployed.constructor(
            market_token_pre.address,
            voting_pre.address,
            parameterizer_opts['price_floor'],
            parameterizer_opts['spread'],
            parameterizer_opts['list_reward'],
            parameterizer_opts['stake'],
            parameterizer_opts['vote_by'],
            parameterizer_opts['plurality'],
            parameterizer_opts['backend_payment'],
            parameterizer_opts['maker_payment'],
            parameterizer_opts['cost_per_byte']
            ).transact()
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    instance = Parameterizer(w3.eth.defaultAccount)
    instance.at(w3, tx_rcpt['contractAddress'])
    return instance

@pytest.fixture(scope='module')
def reserve(w3, ether_token, market_token_pre, parameterizer):
    contract_path = os.path.join(computable.__path__[0], 'contracts')
    with open(os.path.join(contract_path, 'reserve', 'reserve.abi')) as f:
        abi = json.loads(f.read())
    with open(os.path.join(contract_path, 'reserve', 'reserve.bin')) as f:
        bc = f.read()
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    tx_hash = deployed.constructor(ether_token.address, market_token_pre.address,
            parameterizer.address).transact()
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    instance = Reserve(w3.eth.defaultAccount)
    instance.at(w3, tx_rcpt['contractAddress'])
    return instance

@pytest.fixture(scope='module')
def datatrust_pre(w3, ether_token, voting_pre, parameterizer, reserve):
    contract_path = os.path.join(computable.__path__[0], 'contracts')
    with open(os.path.join(contract_path, 'datatrust', 'datatrust.abi')) as f:
        abi = json.loads(f.read())
    with open(os.path.join(contract_path, 'datatrust', 'datatrust.bin')) as f:
        bc = f.read()
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    tx_hash = deployed.constructor(ether_token.address, voting_pre.address,
            parameterizer.address, reserve.address).transact()
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    instance = Datatrust(w3.eth.defaultAccount)
    instance.at(w3, tx_rcpt['contractAddress'])
    return instance

@pytest.fixture(scope='module')
def listing(w3, market_token_pre, voting_pre, parameterizer, datatrust_pre, reserve):
    contract_path = os.path.join(computable.__path__[0], 'contracts')
    with open(os.path.join(contract_path, 'listing', 'listing.abi')) as f:
        abi = json.loads(f.read())
    with open(os.path.join(contract_path, 'listing', 'listing.bin')) as f:
        bc = f.read()
    deployed = w3.eth.contract(abi=abi, bytecode=bc.rstrip('\n'))
    # TODO this will need updating when contracts are updated
    tx_hash = deployed.constructor(market_token_pre.address, voting_pre.address,
            parameterizer.address, reserve.address, datatrust_pre.address).transact()
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    instance = Listing(w3.eth.defaultAccount)
    instance.at(w3, tx_rcpt['contractAddress'])
    return instance

@pytest.fixture(scope='module')
def market_token(w3, market_token_pre, reserve, listing):
    """
    set the privileged for maket_token
    """
    tx_hash = transact(market_token_pre.set_privileged(reserve.address, listing.address))
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    return market_token_pre

@pytest.fixture(scope='module')
def voting(w3, voting_pre, parameterizer, reserve, datatrust_pre, listing):
    tx_hash = transact(voting_pre.set_privileged(parameterizer.address, datatrust_pre.address, listing.address))
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    return voting_pre

@pytest.fixture(scope='module')
def datatrust(w3, datatrust_pre, listing):
    tx_hash = transact(datatrust_pre.set_privileged(listing.address))
    tx_rcpt = w3.eth.waitForTransactionReceipt(tx_hash)
    return datatrust_pre

@pytest.fixture(scope='module')
def flask_app():
    an_app = create_app(celery=c)
    return an_app

@pytest.fixture(scope='function')
def ctx(w3, ether_token, market_token, voting, parameterizer, datatrust, listing, flask_app):
    ctx = flask_app.app_context()
    ctx.push() # current_app and g now are present

    current_app.config['ETHER_TOKEN_CONTRACT_ADDRESS'] = ether_token.address
    current_app.config['MARKET_TOKEN_CONTRACT_ADDRESS'] = market_token.address
    current_app.config['VOTING_CONTRACT_ADDRESS'] = voting.address
    current_app.config['PARAMETERIZER_CONTRACT_ADDRESS'] = parameterizer.address
    current_app.config['DATATRUST_CONTRACT_ADDRESS'] = datatrust.address
    current_app.config['LISTING_CONTRACT_ADDRESS'] = listing.address
    current_app.config['PUBLIC_KEY'] = w3.eth.defaultAccount
    current_app.config['S3_DESTINATION'] = 'Testy_McTestbucket'
    set_w3(w3)

@pytest.fixture(scope='function')
def test_client(ctx):
    """
    The App setup and Flask client for testing
    """
    with current_app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def aws_creds():
    """
    mock the os level creds for moto
    """
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

@pytest.fixture(scope='function')
def dynamo(aws_creds, ctx):
    with mock_dynamodb2():
        db = boto3.resource('dynamodb', current_app.config['REGION'])
        yield db

@pytest.fixture(scope='function')
def create_dynamo_table(aws_creds, ctx, dynamo):
    """
    We have to create the listings table to simulate the staging env
    """
    t = dynamo.create_table(
        TableName=current_app.config['TABLE_NAME'],
        KeySchema=[{
            'AttributeName': 'listing_hash',
            'KeyType': 'HASH'
            }],
        AttributeDefinitions=[{
            'AttributeName': 'listing_hash',
            'AttributeType': 'S'
            }],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
            }
        )

@pytest.fixture(scope='function')
def dynamo_table(aws_creds, ctx, dynamo, create_dynamo_table):
    set_dynamo_table(dynamo)

@pytest.fixture(scope='function')
def s3(aws_creds, ctx):
    with mock_s3():
        s3 = boto3.client('s3', region_name=current_app.config['REGION'])
        yield s3

@pytest.fixture(scope='function')
def s3_bucket(ctx, s3):
    s3.create_bucket(Bucket=current_app.config['S3_DESTINATION'])

@pytest.fixture(scope='function')
def s3_client(s3, s3_bucket):
    set_s3_client(s3)

@pytest.fixture(scope='function')
def cloudwatch_client(ctx, aws_creds):
    with mock_cloudwatch():
        cloudwatch = boto3.client('cloudwatch', region_name=current_app.config['REGION'])
        yield cloudwatch

@pytest.fixture(scope='function')
def mocked_cloudwatch(cloudwatch_client):
    set_cloudwatch(cloudwatch_client)
