from flask import g
from eth_account.messages import encode_defunct

def is_authorized(msg, sig, key):
    """
    Given the proper arguments determine if a message was signed by holder of 'key'
    @param msg: plain text or hashed. The message that was signed
    @param sig: hash Resulting hash from the signature
    @param key: hash signer's public key
    """
    actual = g.w3.eth.account.recover_message(encode_defunct(text=msg), signature=sig)
    return actual.lower() == key.lower()
