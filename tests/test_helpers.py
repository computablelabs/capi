import pytest
from computable.helpers.transaction import call
from apis.helpers import extract_listing_hashes, extract_listing_hashes_to_block, listing_hash_join
from tests.helpers import maybe_transfer_market_token, maybe_increase_market_token_allowance

@pytest.fixture(scope='module')
def logs(w3):
    return [
        {
            'name': 'FooEvent',
            'blockNumber': 1,
            'args': {
            'hash': w3.toBytes(hexstr=w3.toHex(text='foo'))
            }
        },
        {
            'name': 'BarEvent',
            'blockNumber': 2,
            'args': {
            'hash': w3.toBytes(hexstr=w3.toHex(text='bar'))
            }
        },
        {
            'name': 'BazEvent',
            'blockNumber': 4,
            'args': {
            'hash': w3.toBytes(hexstr=w3.toHex(text='baz'))
            }
        },
    ]

def test_maybe_transfer_market_token(w3, market_token):
    user = w3.eth.accounts[1]
    # user should have no bal atm
    bal = call(market_token.balance_of(user))
    assert bal == 0
    # should transfer 10**18 CMT
    one_eth = w3.toWei(1, 'ether')
    tx_rct = maybe_transfer_market_token(w3, market_token, user, one_eth)
    bal = call(market_token.balance_of(user))
    assert bal == one_eth

def test_maybe_increase_market_token_allowance(w3, market_token, voting):
    user = w3.eth.accounts[1]
    # user has not approved the voting contract to spend CMT
    allowed = call(market_token.allowance(user, voting.address))
    assert allowed == 0
    # should allow...
    one_gwei = w3.toWei(1, 'gwei')
    tx_rct = maybe_increase_market_token_allowance(w3, market_token, user, voting.address, one_gwei)
    allowed = call(market_token.allowance(user, voting.address))
    assert allowed == one_gwei

def test_extract_listing_hashes(logs, ctx):
    extracted = extract_listing_hashes(logs)
    assert len(extracted) == 3

def test_extract_listing_hashes_to_block_no_filter_by(logs):
    extracted, tb = extract_listing_hashes_to_block(logs)
    assert len(extracted) == 3
    assert tb == 4

def test_extract_listing_hashes_to_block_filter_by_no_matches(w3, logs):
    filter_by = [w3.toHex(text='spam'), w3.toHex(text='eggs')]
    extracted, tb = extract_listing_hashes_to_block(logs, filter_by)
    assert len(extracted) == 3
    assert tb == 4

def test_extract_listing_hashes_to_block_filter_by_one_match(w3, logs):
    filter_by = [w3.toHex(text='foo')]
    extracted, tb = extract_listing_hashes_to_block(logs, filter_by)
    assert len(extracted) == 2
    assert tb == 4

def test_extract_listing_hashes_to_block_filter_by_two_matches(w3, logs):
    filter_by = [w3.toHex(text='bar'), w3.toHex(text='baz')]
    extracted, tb = extract_listing_hashes_to_block(logs, filter_by)
    assert len(extracted) == 1
    assert tb == 4


def test_extract_listing_hashes_to_block_filter_by_three_matches(w3, logs):
    filter_by = extract_listing_hashes(logs)
    extracted, tb = extract_listing_hashes_to_block(logs, filter_by)
    assert len(extracted) == 0
    assert tb == 4
