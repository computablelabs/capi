import pytest
import json
from eth_account.messages import encode_defunct
from flask import current_app, g
from unittest.mock import patch
from computable.helpers.transaction import call, transact
from core.protocol import has_stake
from apis.delivery.tasks import delivered_async
from apis.delivery.helpers import was_delivered
from tests.helpers import maybe_transfer_market_token, maybe_increase_market_token_allowance, time_travel

def test_jwt_required(test_client, mocked_cloudwatch):
    delivery = test_client.get('/deliveries/')
    assert delivery.status_code == 401

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
    stake = call(parameterizer.get_stake())

    assert has_stake(user)

    # Approve the market token allowance
    old_mkt_allowance = call(market_token.allowance(user, voting.address))
    assert old_mkt_allowance == 0
    tx = transact(market_token.approve(voting.address, w3.toWei(10, 'milliether'), opts={'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    assert rct['status'] == 1
    new_mkt_allowance = call(market_token.allowance(user, voting.address))
    assert new_mkt_allowance == w3.toWei(10, 'milliether')
    assert stake <= new_mkt_allowance

def test_register_datatrust(w3, market_token, voting, parameterizer_opts, datatrust):
    user = w3.eth.defaultAccount
    # register the datatrust
    tx = transact(datatrust.register(current_app.config['DNS_NAME'], {'from': user, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    reg_hash = w3.keccak(text=current_app.config['DNS_NAME'])

    # should see the datatrust candidate now
    is_candidate = call(voting.is_candidate(reg_hash))
    assert is_candidate == True

    # Vote in the datatrust
    voter = w3.eth.accounts[3]
    stake = parameterizer_opts['stake']
    trans_rct = maybe_transfer_market_token(w3, market_token, voter, stake)
    app_rct = maybe_increase_market_token_allowance(w3, market_token, voter, voting.address, stake)
    vote_tx = transact(voting.vote(reg_hash, 1,
        {'from': voter, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    vote_rct = w3.eth.waitForTransactionReceipt(vote_tx)
    # check that the vote registered
    candidate = call(voting.get_candidate(reg_hash))
    assert candidate[4] == 1
    # we need to move forward in time then resolve the vote
    block_now = w3.eth.getBlock(w3.eth.blockNumber)
    time_travel(w3, parameterizer_opts['vote_by'])
    block_later = w3.eth.getBlock(w3.eth.blockNumber)
    assert block_now['timestamp'] < block_later['timestamp']
    assert block_later['timestamp'] > candidate[3]
    did_pass = call(voting.did_pass(reg_hash, parameterizer_opts['plurality']))
    assert did_pass == True

    poll_closed = call(voting.poll_closed(reg_hash))
    assert poll_closed == True

    # resolve the candidate
    res_tx = transact(datatrust.resolve_registration(reg_hash))
    res_rct = w3.eth.waitForTransactionReceipt(res_tx)

    # datatrust should be official
    addr = call(datatrust.get_backend_address())
    assert addr == user

def test_create_listing(w3, market_token, voting, parameterizer_opts, datatrust, listing):
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
    app_rct = maybe_increase_market_token_allowance(w3, market_token, voter, voting.address, stake)
    vote_tx = transact(voting.vote(listing_hash, 1,
        {'from': voter, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    vote_rct = w3.eth.waitForTransactionReceipt(vote_tx)
    time_travel(w3, parameterizer_opts['vote_by'])
    res_tx = transact(listing.resolve_application(listing_hash, {'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    res_rct = w3.eth.waitForTransactionReceipt(res_tx)

    # Confirm the listing in protocol
    ls = call(listing.is_listed(listing_hash))
    assert ls == True

def test_create_and_confirm_buyer(w3, passphrase, ether_token, user):
    # Setup our buyer account, it's going to need some funds
    buyer = w3.eth.accounts[10]
    eth_tx = w3.eth.sendTransaction({
        'to': buyer,
        'from': w3.eth.accounts[0],
        'value': w3.toWei(10, 'ether')
    })
    w3.eth.waitForTransactionReceipt(eth_tx)
    buyer_balance = w3.eth.getBalance(buyer)
    assert buyer_balance == w3.toWei(10, 'ether')

    # Exchange eth for EtherToken
    w3.geth.personal.unlockAccount(buyer, passphrase)
    eth_tx = transact(ether_token.deposit(w3.toWei(5, 'ether'), {'from': buyer, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    eth_rct = w3.eth.waitForTransactionReceipt(eth_tx)
    eth_balance = call(ether_token.balance_of(buyer))
    assert eth_balance == w3.toWei(5, 'ether')

def test_approve_datatrust_spending(w3, ether_token, datatrust, user):
    buyer = w3.eth.accounts[10]
    # Approve datatrust to spend up to 5 EtherToken on the buyer's behalf
    approve_tx = transact(ether_token.approve(datatrust.address, w3.toWei(5, 'ether'),
        {'from': buyer, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    approve_rct = w3.eth.waitForTransactionReceipt(approve_tx)
    approved_amt = call(ether_token.allowance(buyer, datatrust.address))
    assert approved_amt == w3.toWei(5, 'ether')

def test_no_approved_funds_returns_http412(w3, datatrust, dynamo_table, s3_client, user, pk, test_client, mocked_cloudwatch):
    buyer = w3.eth.accounts[10]
    listing_hash = w3.keccak(text='cheap warez')
    file_contents = 'all the cheap warez, pay for shipping and handling only'

    # Store the listing in dynamo
    row = {
            'listing_hash': w3.toHex(listing_hash),
            'title': 'cheap warez',
            'size': len(file_contents.encode('utf-8'))
        }

    g.table.put_item(Item=row)

    # Put the listing in S3
    s3_object = g.s3.put_object(
        Body=file_contents,
        Bucket=current_app.config['S3_DESTINATION'],
        Key=w3.toHex(listing_hash)
    )

    # Request a delivery
    delivery_hash = w3.keccak(text='too_cheap_to_pay_for_it')
    amount = 1 # insufficient bytes for the listing
    delivery_tx = transact(
        datatrust.request_delivery(
            delivery_hash, amount,
            {'from': buyer, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}
        )
    )
    delivery_rct = w3.eth.waitForTransactionReceipt(delivery_tx)
    dlvry = call(datatrust.get_delivery(delivery_hash))
    assert dlvry[0] == buyer

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
        '/deliveries/',
        query_string={
            'delivery_hash': w3.toHex(delivery_hash),
            'query': w3.toHex(listing_hash)
        },
        headers=headers
    )
    assert delivery.status_code == 412

def test_was_not_delivered(w3):
    buyer = w3.eth.accounts[10]
    delivery_hash = w3.keccak(text='monty_pythons_delivery_hash')

    assert not was_delivered(delivery_hash, buyer)

@patch('apis.delivery.deliveries.DeliveryRoute.call_delivered')
def test_successful_delivery(mock_call, w3, ether_token, parameterizer_opts, datatrust, pk, user, dynamo_table, s3_client, test_client, mocked_cloudwatch):
    mock_call.return_value = None # we'll instead call the async method synchronously...
    initial_balance = call(ether_token.balance_of(datatrust.address))
    # Add the listing to dynamo
    buyer = w3.eth.accounts[10]
    listing_hash = w3.keccak(text='a_witch')
    file_contents = 'burn_the_witch'
    mimetype = 'application/text'
    row = {
            'listing_hash': w3.toHex(listing_hash),
            'title': 'so many catz',
            'file_type': mimetype,
            'size': len(file_contents.encode('utf-8'))
        }

    g.table.put_item(Item=row)

    # Put the listing in S3
    s3_object = g.s3.put_object(
        Body=file_contents,
        Bucket=current_app.config['S3_DESTINATION'],
        Key=w3.toHex(listing_hash)
    )

    # Request a delivery
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
    dlvry = call(datatrust.get_delivery(delivery_hash))
    assert dlvry[0] == buyer

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
        '/deliveries/',
        query_string={
            'delivery_hash': w3.toHex(delivery_hash),
            'query': w3.toHex(listing_hash)
        },
        headers=headers
    )

    # things we need to celery method manually
    # delivery_hash -> delivery_hash
    # delivery_url ->  hash any string here
    # listing_accessed transaction hash -> use eth.getTransactionByBlock
    # price_and_time -> use POA defaults here

    # let's assume the transaction is the first one in the latest block
    tx_data = w3.eth.getTransactionByBlock('latest', 0)
    tx_hex = tx_data['hash']

    delivered_async.s(w3.toHex(delivery_hash), w3.toHex(w3.keccak(text='are you suggesting coconuts migrate?')),
        w3.toHex(tx_hex), 2, 600).apply()

    # Datatrust must get paid
    cost_per_byte = parameterizer_opts['cost_per_byte']
    backend_payment = parameterizer_opts['backend_payment']
    final_balance = call(ether_token.balance_of(datatrust.address))
    datatrust_payment = (amount * cost_per_byte * backend_payment) / 100
    assert final_balance - initial_balance == datatrust_payment

    reward = call(datatrust.get_access_reward_earned(listing_hash))
    assert reward == datatrust_payment

    # Assert the listing contents
    mimetype = 'application/text'
    assert delivery.headers['Content-Type'] == mimetype
    assert int(delivery.headers['Content-Length']) == amount
    assert delivery.data == file_contents.encode()
    content_disposition = delivery.headers['Content-Disposition'].split(';')
    assert content_disposition[0] == 'attachment'
    assert content_disposition[1].strip() == f'filename={w3.toHex(listing_hash)}'
    assert delivery.headers['Filename'] == 'so many catz.txt'

    # Ensure downloaded file is removed from Docker container
    with pytest.raises(FileNotFoundError) as exc:
        listing_file = f'{current_app.config["TMP_FILE_STORAGE"]}{w3.toHex(listing_hash)}'
        open(listing_file, 'r')

    # Reading Cloudwatch metrics isn't implemented in moto, but we can at least
    # see that the metrics were put in the g env
    assert len(g.metrics) > 0
    metrics_keys = set()
    for metric in g.metrics:
        for key in metric.keys():
            metrics_keys.add(key)
    assert 'get_delivery' in metrics_keys
    assert 'get_bytes_purchased' in metrics_keys
    assert 'listing_accessed' in metrics_keys
    assert 'delivered' in metrics_keys
    assert 'get_listing_mimetype_size_and_title' in metrics_keys
    assert 'get_listing_and_meta' in metrics_keys

def test_was_delivered(w3):
    buyer = w3.eth.accounts[10]
    delivery_hash = w3.keccak(text='monty_pythons_delivery_hash')

    assert was_delivered(delivery_hash, buyer)
