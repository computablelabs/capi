from io import BytesIO
import json
import pytest
from unittest.mock import patch
from flask import current_app, g
from computable.helpers.transaction import call, transact
from computable.contracts.constants import PLURALITY
from tests.helpers import maybe_transfer_market_token, maybe_increase_market_token_approval, time_travel
from apis.listing.tasks import send_data_hash_after_mining

# OWNER, MAKER, VOTER, DATATRUST = accounts [0,1,2,0]

def test_register_and_confirm(w3, market_token, voting, parameterizer_opts, datatrust):
    tx = transact(datatrust.register(current_app.config['DNS_NAME'], {'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    rct = w3.eth.waitForTransactionReceipt(tx)

    reg_hash = w3.keccak(text=current_app.config['DNS_NAME'])

    # should see the candidate now
    is_candidate = call(voting.is_candidate(reg_hash))
    assert is_candidate == True

    # we'll use acct 2 as voter, will likely need market token...
    voter = w3.eth.accounts[2]
    stake = parameterizer_opts['stake']
    trans_rct = maybe_transfer_market_token(w3, market_token, voter, stake)
    # will likely need to approve voting
    app_rct = maybe_increase_market_token_approval(w3, market_token, voter, voting.address, stake)
    # should be able to vote now
    vote_tx = transact(voting.vote(reg_hash, 1,
        {'from': voter, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    vote_rct = w3.eth.waitForTransactionReceipt(vote_tx)
    # check that the vote registered
    candidate = call(voting.get_candidate(reg_hash))
    assert candidate[4] == 1
    # we need to move forward in time then resolve the vote
    block_now = w3.eth.getBlock(w3.eth.blockNumber)
    time_travel(w3, parameterizer_opts['vote_by'])
    block_later = w3.eth.getBlock(w3.eth.blockNumber)
    assert block_now['timestamp'] < block_later['timestamp']
    assert block_later['timestamp'] > candidate[3]
    did_pass = call(voting.did_pass(reg_hash, parameterizer_opts['plurality']))
    assert did_pass == True

    poll_closed = call(voting.poll_closed(reg_hash))
    assert poll_closed == True

    # resolve the candidate
    res_tx = transact(datatrust.resolve_registration(reg_hash))
    res_rct = w3.eth.waitForTransactionReceipt(res_tx)

    # datatrust should be official
    addr = call(datatrust.get_backend_address())
    assert addr == w3.eth.defaultAccount

def test_get_listings(w3, market_token, voting, parameterizer_opts, datatrust, listing, test_client, dynamo_table, s3_client):
    # needs to be a candidate first...
    maker = w3.eth.accounts[1]
    listing_hash = w3.keccak(text='testytest123')
    tx = transact(listing.list(listing_hash, {'from': maker, 'gas_price': w3.toWei(2, 'gwei'), 'gas': 1000000}))
    rct = w3.eth.waitForTransactionReceipt(tx)

    #  logs = voting.deployed.events.CandidateAdded().processReceipt(rct)
    #  print(logs)

    is_candidate = call(voting.is_candidate(listing_hash))
    assert is_candidate == True

    # the registered datatrust needs to set the data hash
    data_hash = w3.keccak(text='datanadmoardata')
    dtx = transact(datatrust.set_data_hash(listing_hash, data_hash,
        {'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    drct = w3.eth.waitForTransactionReceipt(dtx)
    # the data hash must be set or the listing will fail
    # TODO computable.py needs to implement get_data_hash
    check_data_hash = datatrust.deployed.functions.getDataHash(listing_hash).call()
    assert check_data_hash == data_hash

    # we'll use acct 2 as voter, will likely need market token...
    voter = w3.eth.accounts[2]
    stake = parameterizer_opts['stake']
    trans_rct = maybe_transfer_market_token(w3, market_token, voter, stake)
    # will likely need to approve voting
    app_rct = maybe_increase_market_token_approval(w3, market_token, voter, voting.address, stake)
    # should be able to vote now
    vote_tx = transact(voting.vote(listing_hash, 1,
        {'from': voter, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    vote_rct = w3.eth.waitForTransactionReceipt(vote_tx)
    # check that the vote registered
    candidate = call(voting.get_candidate(listing_hash))
    assert candidate[4] == 1
    # we need to move forward in time then resolve the vote
    block_now = w3.eth.getBlock(w3.eth.blockNumber)
    time_travel(w3, parameterizer_opts['vote_by'])
    block_later = w3.eth.getBlock(w3.eth.blockNumber)
    assert block_now['timestamp'] < block_later['timestamp']
    assert block_later['timestamp'] > candidate[3]

    did_pass = call(voting.did_pass(listing_hash, parameterizer_opts['plurality']))
    assert did_pass == True

    poll_closed = call(voting.poll_closed(listing_hash))
    assert poll_closed == True

    res_tx = transact(listing.resolve_application(listing_hash, {'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    res_rct = w3.eth.waitForTransactionReceipt(res_tx)

    # should be listed
    is_listed = call(listing.is_listed(listing_hash))
    assert is_listed == True

    #  logs = listing.deployed.events.ApplicationFailed().processReceipt(res_rct)
    #  print(logs)

    # must exist in the dynamo table
    row = {
            'listing_hash': w3.toHex(listing_hash),
            'title': 'lol catz 9000'
        }

    g.table.put_item(Item=row)

    # store in S3
    file_contents = 'so many catz #lolz #hashtag #9000 #allthecatz'
    s3_object = g.s3.put_object(
        Body=file_contents,
        Bucket=current_app.config['S3_DESTINATION'],
        Key=w3.toHex(listing_hash)
    )

    listings = test_client.get('/listings/')
    payload = json.loads(listings.data)
    assert listings.status_code == 200
    assert payload['from_block'] == 0
    assert payload['items'][0]['listing_hash'] == w3.toHex(listing_hash) # payload hashes are hex
    assert payload['items'][0]['title'] == 'lol catz 9000'
    assert payload['items'][0]['size'] == len(file_contents.encode('utf-8'))
    assert payload['to_block'] > 0

@patch('apis.listing.listings.ListingsRoute.send_data_hash')
def test_post_listings(mock_send, w3, voting, datatrust, listing, test_client, s3_client, dynamo_table):
    # the mocked send_data_hash method must return a uuid, so fake it here
    mock_send.return_value = '123-abc'

    # Create a listing to get tx_hash
    maker = w3.eth.accounts[1]
    listing_hash = w3.keccak(text='test_post_listing')
    tx = transact(listing.list(listing_hash, {'from': maker, 'gas_price': w3.toWei(2, 'gwei'), 'gas': 1000000}))
    rct = w3.eth.waitForTransactionReceipt(tx)

    test_payload = {
        'tx_hash': w3.toHex(tx),
        'title': 'My Bestest Pony',
        'license': 'MIT',
        'file_type': 'gif',
        'md5_sum': '7f7c47e44b125f2944cb0879cbe428ce',
        'listing_hash': w3.toHex(listing_hash),
        'file': (BytesIO(b'a pony'), 'my_little_pony.gif'),
        'description': 'mah pony is mah pony',
        'owner': maker
    }

    listing = test_client.post('/listings/',
    content_type='multipart/form-data',
    data=test_payload)

    mock_send.assert_called_once_with(
        w3.toHex(tx),
        w3.toHex(listing_hash),
        '0xadc113d55e8b7d4a4e132b1f24adcef15f4a4d011cb83b7e08d865538fd4bdf5'
    )

    assert listing.status_code == 201
    payload = json.loads(listing.data)
    assert payload['task_id'] == '123-abc'

    uploaded_file = g.s3.get_object(
        Bucket=current_app.config['S3_DESTINATION'],
        Key=w3.toHex(listing_hash)
    )['Body'].read().decode()
    assert uploaded_file == 'a pony'

    new_listing = g.table.get_item(
        Key={
            'listing_hash': w3.toHex(listing_hash)
        }
    )
    assert new_listing['Item']['listing_hash'] == test_payload['listing_hash']
    assert new_listing['Item']['title'] == test_payload['title']
    assert new_listing['Item']['description'] == test_payload['description']
    assert new_listing['Item']['license'] == test_payload['license']
    assert new_listing['Item']['file_type'] == test_payload['file_type']
    assert new_listing['Item']['md5_sum'] == test_payload['md5_sum']
    assert new_listing['Item']['owner'] == test_payload['owner']

def test_send_data_hash_after_mining(w3, listing, datatrust, voting, test_client):
    """
    Test that the data hash is set for a completed listing candidate
    """
    # Create a listing candidate for testing
    maker = w3.eth.accounts[1]
    listing_hash = w3.keccak(text='test_hash_after_mining')
    tx = transact(listing.list(listing_hash, {'from': maker, 'gas_price': w3.toWei(2, 'gwei'), 'gas': 1000000}))

    data_hash = w3.toHex(w3.keccak(text='test_data_hash'))

    # Use the celery task to set the data hash. we can run it synchronously and bypass testing celery, which we can assume works
    task = send_data_hash_after_mining.s(tx, listing_hash, data_hash).apply()

    # looks to be a uuid of some sort. TODO what exacly is this?
    assert task != None
    # Verify the data hash in the candidate from protocol
    check_data_hash = w3.toHex(datatrust.deployed.functions.getDataHash(listing_hash).call())
    assert check_data_hash == data_hash
