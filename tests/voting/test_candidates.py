import json
import pytest
from flask import g
from computable.helpers.transaction import call, transact
from computable.contracts.constants import PLURALITY

def test_get_candidates_application(w3, voting, listing, test_client, dynamo_table, mocked_cloudwatch):
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

    # Reading Cloudwatch metrics isn't implemented in moto, but we can at least
    # see that the metrics were put in the g env
    assert len(g.metrics) > 0
    metrics_keys = set()
    for metric in g.metrics:
        for key in metric.keys():
            metrics_keys.add(key)
    assert 'get_voting' in metrics_keys
    assert 'extract_listing_hashes' in metrics_keys
    assert 'extract_listing_hashes_to_block' in metrics_keys

def test_get_candidate(w3, test_client, dynamo_table, mocked_cloudwatch):
    # we'll just re-use the above candidate...
    b = w3.keccak(text='testytest123')
    applicant = w3.toHex(b)

    # we re-create the dynamo table per function TODO should we use 'module' ?
    row = {
            'listing_hash': applicant,
            'title': 'I can haz application',
            'description': 'catz applying for listings',
            'license': 'GFU',
            'file_type': 'gif',
            'size': 1000
        }

    g.table.put_item(Item=row)

    candidate = test_client.get(f'/candidates/application/{applicant}')
    payload = json.loads(candidate.data)
    assert candidate.status_code == 200
    assert payload['kind'] == 1
    assert payload['listing_hash'] == applicant
    assert payload['title'] == 'I can haz application'
    assert payload['size'] == 1000

    # Reading Cloudwatch metrics isn't implemented in moto, but we can at least
    # see that the metrics were put in the g env
    assert len(g.metrics) > 0
    metrics_keys = set()
    for metric in g.metrics:
        for key in metric.keys():
            metrics_keys.add(key)
    assert 'get_voting' in metrics_keys
    assert 'get_application' in metrics_keys

def test_has_ethertoken(w3, ether_token):
    user = w3.eth.defaultAccount
    user_bal = call(ether_token.balance_of(user))
    assert user_bal == 0

    # Deposit ETH in EtherToken
    tx = transact(ether_token.deposit(
        w3.toWei(10, 'ether'), {'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    new_user_bal = call(ether_token.balance_of(user))
    assert new_user_bal == w3.toWei(10, 'ether')
    assert rct['status'] == 1

def test_has_cmt(w3, ether_token, market_token, reserve):
    user = w3.eth.defaultAccount
    # Approve the spend
    user_bal = call(ether_token.balance_of(user))
    old_allowance = call(ether_token.allowance(user, reserve.address))
    assert old_allowance == 0
    tx= transact(ether_token.approve(reserve.address, w3.toWei(10, 'ether'), opts={'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    assert rct['status'] == 1
    new_allowance = call(ether_token.allowance(user, reserve.address))
    assert new_allowance == w3.toWei(10, 'ether')

    # Perform pre-checks for support
    support_price = call(reserve.get_support_price())
    assert user_bal >= support_price
    assert new_allowance >= user_bal
    minted = (user_bal // support_price) * 10**9
    assert minted == 10**7 * w3.toWei(1, 'gwei')
    priv = call(market_token.has_privilege(reserve.address))
    assert priv == True
    total_supply = call(market_token.total_supply())
    assert total_supply == w3.toWei(4, 'ether')

    # Call support
    tx = transact(reserve.support(user_bal, opts={'gas': 1000000, 'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    assert rct['status'] == 1
    cmt_user_bal = call(market_token.balance_of(user))
    # There is the creator already
    assert cmt_user_bal >= w3.toWei(10, 'milliether')
    new_supply = call(market_token.total_supply())
    assert new_supply == total_supply + w3.toWei(10, 'milliether')

def test_can_stake(w3, market_token, voting, parameterizer):
    user = w3.eth.defaultAccount

    cmt_user_bal = call(market_token.balance_of(user))
    stake = call(parameterizer.get_stake())
    assert stake <= cmt_user_bal

    # Approve the market token allowance
    old_mkt_allowance = call(market_token.allowance(user, voting.address))
    assert old_mkt_allowance == 0
    tx = transact(market_token.approve(voting.address, w3.toWei(10, 'milliether'), opts={'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    assert rct['status'] == 1
    new_mkt_allowance = call(market_token.allowance(user, voting.address))
    assert new_mkt_allowance == w3.toWei(10, 'milliether')
    assert stake <= new_mkt_allowance


def test_get_candidates_non_application(w3, ether_token, market_token,  voting, parameterizer, reserve, mocked_cloudwatch, test_client):
    user = w3.eth.defaultAccount

    # reparam here as our non application
    tx = transact(parameterizer.reparameterize(PLURALITY, 51, {'from': user, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    hash = call(parameterizer.get_hash(PLURALITY, 51))

    is_candidate = call(voting.is_candidate(hash))
    assert is_candidate == True

    candidates = test_client.get('/candidates/')
    payload = json.loads(candidates.data)
    assert candidates.status_code == 200
    assert payload['from_block'] == 0
    # there are 2 candidates counting the applicaton above
    assert len(payload['items']) == 2
    # this reparam is the newest
    assert payload['items'][1] == w3.toHex(hash) # payload hashes are hex
    assert payload['to_block'] > 0

    # Reading Cloudwatch metrics isn't implemented in moto, but we can at least
    # see that the metrics were put in the g env
    assert len(g.metrics) > 0
    metrics_keys = set()
    for metric in g.metrics:
        for key in metric.keys():
            metrics_keys.add(key)
    assert 'get_voting' in metrics_keys
    assert 'extract_listing_hashes' in metrics_keys
    assert 'extract_listing_hashes_to_block' in metrics_keys
