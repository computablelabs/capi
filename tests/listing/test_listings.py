import json
import pytest
from flask import current_app, g
from computable.helpers.transaction import call, transact
from computable.contracts.constants import PLURALITY
from tests.helpers import maybe_transfer_market_token, maybe_increase_market_token_approval, time_travel

# OWNER, MAKER, VOTER, DATATRUST = accounts [0,1,2,3]

def test_register_and_confirm(w3, market_token, voting, parameterizer_opts, datatrust):
    dt = w3.eth.accounts[3]
    tx = transact(datatrust.register(current_app.config['DNS_NAME'], {'from': dt, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
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
    assert addr == dt

def test_get_listings(w3, market_token, voting, parameterizer_opts, datatrust, listing, test_client, dynamo_table):
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
    dt = w3.eth.accounts[3]
    data_hash = w3.keccak(text='datanadmoardata')
    dtx = transact(datatrust.set_data_hash(listing_hash, data_hash,
        {'from': dt, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
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

    listings = test_client.get('/listings/')
    payload = json.loads(listings.data)
    assert listings.status_code == 200
    assert payload['from_block'] == 0
    assert payload['items'][0]['listing_hash'] == w3.toHex(listing_hash) # payload hashes are hex
    assert payload['items'][0]['title'] == 'lol catz 9000'
    assert payload['to_block'] > 0

def test_post_listings(listing, test_client):
    listing = test_client.post('/listings/')
    assert listing.status_code == 201
