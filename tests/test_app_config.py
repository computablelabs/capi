import pytest
from app import app

def test_config():
    assert app.config['TESTING'] == True
    assert app.config['DEBUG'] == True
    assert app.config['SECRET_KEY'] == 'Th1s1sS0meS3cr3tSh1tR1ghtH3r3'

def test_get_client(client):
    """
    quick sanity check on app
    """
    assert client != None
