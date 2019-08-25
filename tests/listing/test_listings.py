import json
import pytest
from computable.helpers.transaction import call, transact
from computable.contracts.constants import PLURALITY
from tests.helpers import maybe_transfer_market_token, maybe_increase_market_token_approval, time_travel

def test_get_listings(w3, market_token, voting, parameterizer_opts, listing, test_client):
    # needs to be a candidate first...
    maker = w3.eth.accounts[1]
    listing_hash = w3.keccak(text='testytest123')
    tx = transact(listing.list(listing_hash, {'from': maker, 'gas_price': w3.toWei(2, 'gwei'), 'gas': 1000000}))
    rct = w3.eth.waitForTransactionReceipt(tx)

    is_candidate = call(voting.is_candidate(listing_hash))
    assert is_candidate == True

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

    #  res_tx = transact(listing.resolve_application(listing_hash))
    #  res_rct = w3.eth.waitForTransactionReceipt(res_tx)
    # should be listed
    #  is_listed = call(listing.is_listed(listing_hash))
    #  assert is_listed == True

    #  listings = test_client.get('/listings/')
    #  payload = json.loads(candidates.data)
    #  assert candidates.status_code == 200
    #  assert payload['from_block'] == 0
    #  assert payload['items'][0] == w3.toHex(listing_hash) # payload hashes are hex
    #  assert payload['to_block'] > 0
