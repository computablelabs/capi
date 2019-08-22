from flask import current_app, g
import pytest

def test_config(ether_token, voting, datatrust, listing, ctx):
    with ctx:
        assert current_app.config['TESTING'] == True
        assert current_app.config['DEBUG'] == True
        assert current_app.config['SECRET_KEY'] == 'Th1s1sS0meS3cr3tSh1tR1ghtH3r3'

        assert g.ether_token_address == ether_token.address
        assert g.voting_address == voting.address
        assert g.datatrust_address == datatrust.address
        assert g.listing_address == listing.address
        assert len(g.w3.eth.defaultAccount) == 42

def test_get_client(test_client):
    """
    quick sanity check on app
    """
    assert test_client != None
