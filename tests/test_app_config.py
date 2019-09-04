from flask import current_app, g
import pytest

def test_config(ether_token, voting, datatrust, listing, ctx):
    assert current_app.config['TESTING'] == True
    assert current_app.config['DEBUG'] == True

    assert current_app.config['ETHER_TOKEN_CONTRACT_ADDRESS'] == ether_token.address
    assert current_app.config['VOTING_CONTRACT_ADDRESS'] == voting.address
    assert current_app.config['DATATRUST_CONTRACT_ADDRESS'] == datatrust.address
    assert current_app.config['LISTING_CONTRACT_ADDRESS'] == listing.address
    assert len(g.w3.eth.defaultAccount) == 42

def test_get_client(test_client):
    """
    quick sanity check on test_client
    """
    assert test_client != None
