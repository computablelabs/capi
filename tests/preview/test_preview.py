import pytest
import json
from eth_account.messages import encode_defunct
from flask import current_app, g
from computable.helpers.transaction import call, send, transact
from core import constants as C
from core.protocol import has_stake
from tests.helpers import maybe_transfer_market_token, maybe_increase_market_token_allowance, time_travel

def test_custom_user_hash_eth(w3, ctx, user):
    tx = w3.eth.sendTransaction({'from': w3.eth.accounts[0], 'to': user, 'gas': 1000000,
        'gasPrice': w3.toWei(2, 'gwei'), 'value': w3.toWei(3, 'ether')})
    rct = w3.eth.waitForTransactionReceipt(tx)
    assert rct['status'] == 1
    assert w3.eth.getBalance(user) > 0

def test_has_cmt(w3, pk, user, ether_token, market_token, reserve):
    maybe_transfer_market_token(w3, market_token, user, w3.toWei(1, 'ether'))
    cmt_user_bal = call(market_token.balance_of(user))
    assert cmt_user_bal == w3.toWei(1, 'ether')

def test_can_stake(user):
    assert has_stake(user)

def test_register_datatrust(w3, market_token, voting, parameterizer_opts, datatrust):
    user = w3.eth.defaultAccount
    # user should already be able to stake
    assert has_stake(user)

    # register the datatrust, allowance first
    maybe_increase_market_token_allowance(w3, market_token, user, voting.address, w3.toWei(1, 'ether'))

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

def test_create_candidate(w3, voting, datatrust, listing):
    maker = w3.eth.accounts[1]
    listing_hash = w3.keccak(text='We Want. A shrubbery!')
    tx = transact(listing.list(listing_hash, {'from': maker, 'gas_price': w3.toWei(2, 'gwei'), 'gas': 1000000}))
    rct = w3.eth.waitForTransactionReceipt(tx)

    # Set the datahash
    file_contents = 'Roger. Roger The Shrubber.'
    data_hash = w3.keccak(text=file_contents)
    dtx = transact(datatrust.set_data_hash(listing_hash, data_hash,
        {'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    drct = w3.eth.waitForTransactionReceipt(dtx)

    assert call(voting.candidate_is(listing_hash, C.candidate_kinds['application']))

def test_preview(w3, pk, user, dynamo_table, s3_client, test_client, mocked_cloudwatch):
    assert has_stake(user)

    listing_hash = w3.keccak(text='We Want. A shrubbery!')
    file_contents = 'Roger. Roger The Shrubber.'

    mimetype = 'application/text'
    row = {
            'listing_hash': w3.toHex(listing_hash),
            'title': 'The Nights Who Formerly Said Ni',
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

    #  # Get a jwt
    msg = 'Ooh, that looks very nice'
    signed = w3.eth.account.sign_message(encode_defunct(text=msg), private_key=pk)

    login = test_client.post('/authorize/', json={
        'message': msg,
        'signature': w3.toHex(signed.signature),
        'public_key': user
    })
    payload = json.loads(login.data)
    access_token = payload['access_token']

    # Get the preview...
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    preview = test_client.get(f'/previews/{w3.toHex(listing_hash)}', headers=headers)

    assert preview.headers['Content-Type'] == 'application/text'
    assert preview.data == file_contents.encode()

    content_disposition = preview.headers['Content-Disposition'].split(';')
    assert content_disposition[0] == 'attachment'

    # Ensure downloaded file is removed from Docker container
    with pytest.raises(FileNotFoundError) as exc:
        listing_file = f'{current_app.config["TMP_FILE_STORAGE"]}{w3.toHex(listing_hash)}'
        open(listing_file, 'r')
