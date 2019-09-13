import json
import pytest
from flask import g
from computable.helpers.transaction import call, transact
from computable.contracts.constants import PLURALITY

def test_get_candidates_application(w3, voting, listing, test_client, dynamo_table):
    maker = w3.eth.accounts[1]
    listing_hash = w3.keccak(text='testytest123')
    tx = transact(listing.list(listing_hash, {'from': maker, 'gas_price': w3.toWei(2, 'gwei'), 'gas': 1000000}))
    rct = w3.eth.waitForTransactionReceipt(tx)

    is_candidate = call(voting.is_candidate(listing_hash))
    assert is_candidate == True

    # we can seed the dynamo table directly...
    row = {
            'listing_hash': w3.toHex(listing_hash),
            'title': 'so many catz'
        }

    g.table.put_item(Item=row)

    candidates = test_client.get('/candidates/application')
    payload = json.loads(candidates.data)
    assert candidates.status_code == 200
    assert payload['from_block'] == 0
    assert payload['items'][0]['listing_hash'] == w3.toHex(listing_hash) # payload hashes are hex
    assert payload['items'][0]['title'] == 'so many catz'
    assert payload['to_block'] > 0

def test_get_candidates_non_application(w3, voting, parameterizer, test_client):
    # reparam here as our non application
    tx = transact(parameterizer.reparameterize(PLURALITY, 51))
    rct = w3.eth.waitForTransactionReceipt(tx)
    #  logs = parameterizer.deployed.events.ReparamProposed().processReceipt(rct)
    hash = call(parameterizer.get_hash(PLURALITY, 51))
    #  assert logs[0]['args']['hash'] == hash

    is_candidate = call(voting.is_candidate(hash))
    assert is_candidate == True

    candidates = test_client.get('/candidates/')
    payload = json.loads(candidates.data)
    assert candidates.status_code == 200
    assert payload['from_block'] == 0
    assert payload['items'][0] == w3.toHex(hash) # payload hashes are hex
    assert payload['to_block'] > 0
