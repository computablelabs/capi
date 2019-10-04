from eth_account.messages import encode_defunct
from apis.authorize.helpers import is_authorized
from core import constants as C

# user fixture adds the custom user to accounts
def test_valid_user(w3, user):
    assert len(w3.eth.accounts) == 11

def test_is_authorized(w3, pk, user, ctx):
    msg = 'She turned me into a newt.'
    signed = w3.eth.account.sign_message(encode_defunct(text=msg), private_key=pk)
    assert is_authorized(msg, signed.signature, w3.eth.accounts[10]) == True
