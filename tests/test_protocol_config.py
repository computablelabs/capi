import pytest
from computable.helpers.transaction import call

def test_w3(w3):
    """
    Is web3 correctly setup for testing?
    """
    assert w3.eth.defaultAccount == w3.eth.accounts[0]

def test_ether_token_deploy(ether_token):
    """
    did the ether token deploy correctly?
    """
    assert len(ether_token.account) == 42
    assert len(ether_token.address) == 42
    assert ether_token.account != ether_token.address

def test_market_token_deploy(market_token_pre):
    """
    did the market token deploy correctly?
    """
    assert len(market_token_pre.account) == 42
    assert len(market_token_pre.address) == 42
    assert market_token_pre.account != market_token_pre.address

def test_voting_deploy(voting_pre):
    """
    did the voting contract deploy correctly?
    """
    assert len(voting_pre.account) == 42
    assert len(voting_pre.address) == 42
    assert voting_pre.account != voting_pre.address

def test_voting_is_candidate_falsy(w3, voting_pre):
    hash = w3.keccak(text='nope')
    assert call(voting_pre.is_candidate(hash)) == False

def test_p11r_deploy(parameterizer):
    """
    did the p11r contract deploy correctly?
    """
    assert len(parameterizer.account) == 42
    assert len(parameterizer.address) == 42
    assert parameterizer.account != parameterizer.address

def test_reserve_deploy(reserve):
    """
    did the reserve contract deploy correctly?
    """
    assert len(reserve.account) == 42
    assert len(reserve.address) == 42
    assert reserve.account != reserve.address

def test_datatrust_deploy(datatrust_pre):
    """
    did the datatrust contract deploy correctly?
    """
    assert len(datatrust_pre.account) == 42
    assert len(datatrust_pre.address) == 42
    assert datatrust_pre.account != datatrust_pre.address

def test_listing_deploy(listing):
    """
    did the reserve contract deploy correctly?
    """
    assert len(listing.account) == 42
    assert len(listing.address) == 42
    assert listing.account != listing.address

def test_market_token_set_priv(market_token, reserve, listing):
    tup = call(market_token.get_privileged())
    assert tup[0] == reserve.address
    assert tup[1] == listing.address

def test_voting_set_priv(voting, parameterizer, reserve, datatrust_pre, listing):
    tup = call(voting.get_privileged())
    assert tup[0] == parameterizer.address
    assert tup[1] == datatrust_pre.address
    assert tup[2] == listing.address

def test_datatrust_set_priv(datatrust, listing):
    addr = call(datatrust.get_privileged())
    assert addr == listing.address
