import pytest
from computable.helpers.transaction import call
from tests.helpers import maybe_transfer_market_token, maybe_increase_market_token_approval

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

def test_maybe_increase_market_token_approval(w3, market_token, voting):
    user = w3.eth.accounts[1]
    # user has not approved the voting contract to spend CMT
    allowed = call(market_token.allowance(user, voting.address))
    assert allowed == 0
    # should allow...
    one_gwei = w3.toWei(1, 'gwei')
    tx_rct = maybe_increase_market_token_approval(w3, market_token, user, voting.address, one_gwei)
    allowed = call(market_token.allowance(user, voting.address))
    assert allowed == one_gwei
