import json
import pytest
from computable.helpers.transaction import call, transact
from computable.contracts.constants import PLURALITY

def test_get_candidates(w3, voting, listing, test_client):
    # (p11r saving here for posterity)
    #  tx = transact(parameterizer.reparameterize(PLURALITY, 51))
    #  rct = w3.eth.waitForTransactionReceipt(tx)
    #  logs = parameterizer.deployed.events.ReparamProposed().processReceipt(rct)
    #  hash = call(parameterizer.get_hash(PLURALITY, 51))
    #  assert logs[0]['args']['hash'] == hash

    maker = w3.eth.accounts[1]
    listing_hash = w3.keccak(text='testytest123')
    tx = transact(listing.list(listing_hash, {'from': maker, 'gas_price': w3.toWei(2, 'gwei'), 'gas': 1000000}))
    rct = w3.eth.waitForTransactionReceipt(tx)

    is_candidate = call(voting.is_candidate(listing_hash))
    assert is_candidate == True

    candidates = test_client.get('/candidates/')
    payload = json.loads(candidates.data)
    assert candidates.status_code == 200
    assert payload['from_block'] == 0
    assert payload['items'][0] == w3.toHex(listing_hash) # payload hashes are hex
    assert payload['to_block'] > 0

def test_get_candidates_application(w3, test_client):
    # if calling for an application we should get back the same candidate as above
    listing_hash = w3.keccak(text='testytest123')

    candidates = test_client.get('/candidates/application')
    payload = json.loads(candidates.data)
    assert candidates.status_code == 200
    assert payload['kind'] == 1
    assert payload['from_block'] == 0
    assert payload['items'][0] == w3.toHex(listing_hash) # payload hashes are hex
    assert payload['to_block'] > 0
