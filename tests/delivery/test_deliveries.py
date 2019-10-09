import pytest
import json
from eth_account.messages import encode_defunct
from flask import current_app, g
from computable.helpers.transaction import call, transact
from tests.helpers import maybe_transfer_market_token, maybe_increase_market_token_approval, time_travel

def test_jwt_required(test_client):
    delivery = test_client.get('/deliveries/asdf')
    assert delivery.status_code == 401

def test_successful_delivery(w3, listing, datatrust, parameterizer_opts, market_token, voting, s3_client, pk, user, passphrase, dynamo_table, test_client):
    # Create a candidate
    maker = w3.eth.accounts[1]
    listing_hash = w3.keccak(text='a_witch')
    tx = transact(listing.list(listing_hash, {'from': maker, 'gas_price': w3.toWei(2, 'gwei'), 'gas': 1000000}))
    rct = w3.eth.waitForTransactionReceipt(tx)

    # Set the datahash
    file_contents = 'burn_the_witch'
    data_hash = w3.keccak(text=file_contents)
    dtx = transact(datatrust.set_data_hash(listing_hash, data_hash,
        {'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    drct = w3.eth.waitForTransactionReceipt(dtx)
    
    # Vote in the listing
    voter = w3.eth.accounts[2]
    stake = parameterizer_opts['stake']
    trans_rct = maybe_transfer_market_token(w3, market_token, voter, stake)
    app_rct = maybe_increase_market_token_approval(w3, market_token, voter, voting.address, stake)
    vote_tx = transact(voting.vote(listing_hash, 1,
        {'from': voter, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    vote_rct = w3.eth.waitForTransactionReceipt(vote_tx)
    time_travel(w3, parameterizer_opts['vote_by'])
    res_tx = transact(listing.resolve_application(listing_hash, {'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    res_rct = w3.eth.waitForTransactionReceipt(res_tx)

    # Put the listing in S3
    g.s3.create_bucket(
        Bucket='ffa-tests'
    )
    s3_object = g.s3.put_object(
        Body=file_contents,
        Bucket=current_app.config['S3_DESTINATION'],
        Key=w3.toHex(listing_hash)
    )

    # Add the listing to dynamo
    mimetype = 'application/text'
    row = {
            'listing_hash': w3.toHex(listing_hash),
            'title': 'so many catz',
            'file_type': mimetype
        }

    g.table.put_item(Item=row)

    # Setup our buyer account, it's going to need some funds
    buyer = w3.eth.accounts[10]
    eth_tx = w3.eth.sendTransaction({
        'to': buyer,
        'from': w3.eth.accounts[0],
        'value': w3.toWei(1, 'ether')
    })
    w3.eth.waitForTransactionReceipt(eth_tx)
    
    # Request a delivery
    w3.geth.personal.unlockAccount(buyer, passphrase)
    delivery_hash = w3.keccak(text='monty_pythons_delivery_hash')
    amount = 14 # derived from storing the actual file in S3 and checking size
    delivery_tx = transact(
        datatrust.request_delivery(
            delivery_hash, amount, 
            {'from': buyer, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}
        )
    )
    w3.geth.personal.lockAccount(buyer)
    delivery_rct = w3.eth.waitForTransactionReceipt(delivery_tx)
    dlvry = datatrust.get_delivery(delivery_hash)

    # Get a jwt
    msg = 'weighs as much as a duck'
    signed = w3.eth.account.sign_message(encode_defunct(text=msg), private_key=pk)
    login = test_client.post('/authorize/', json={
        'message': msg,
        'signature': w3.toHex(signed.signature),
        'public_key': buyer
    })
    payload = json.loads(login.data)
    access_token = payload['access_token']

    # Get the listing
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    delivery = test_client.get(
        f'/deliveries/{w3.toHex(delivery_hash)}',
        query_string={'listing_hash': w3.toHex(listing_hash)},
        headers=headers
    )
    #TODO: Assert delivered in protocol
    bytes_accessed = call(datatrust.get_bytes_accessed(delivery_hash))
    # assert bytes_accessed == amount # uncomment once request_delivery is resolved

    # Assert the listing contents
    assert delivery.headers['Content-Type'] == mimetype
    assert int(delivery.headers['Content-Length']) == amount
    assert delivery.data == file_contents.encode()
