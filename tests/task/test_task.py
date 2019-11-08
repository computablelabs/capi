import json
import pytest
from flask import current_app
from unittest.mock import patch
from computable.helpers.transaction import call, transact
from computable.contracts.constants import PLURALITY
import core.constants as C
from core.protocol import has_stake
from tests.helpers import maybe_transfer_market_token, maybe_increase_market_token_allowance, time_travel

class MockTask:
    status=None

    def __init__(self, status):
        self.status = status

    def get(self, timeout):
        return timeout

    def forget(self):
        pass

@patch('apis.task.tasks.TaskRoute.get_task')
def test_get_pending_task(mock_get_task, test_client):
    mock_get_task.return_value = MockTask(C.PENDING)
    id = 'abcd-1234'

    response = test_client.get(f'/tasks/{id}')
    mock_get_task.assert_called_once_with(id)

    assert response.status_code == 200

    payload = json.loads(response.data)
    assert payload['message'] == (C.CELERY_TASK_FETCHED % id)
    assert payload['status'] == C.PENDING
    assert payload['result'] == None

@patch('apis.task.tasks.TaskRoute.get_task')
def test_get_successful_task(mock_get_task, test_client):
    mock_get_task.return_value = MockTask(C.SUCCESS)
    id = 'abcd-2345'

    response = test_client.get(f'/tasks/{id}')
    mock_get_task.assert_called_once_with(id)

    assert response.status_code == 200

    payload = json.loads(response.data)
    assert payload['message'] == (C.CELERY_TASK_FETCHED % id)
    assert payload['status'] == C.SUCCESS
    assert float(payload['result']) == C.CELERY_TASK_TIMEOUT

@patch('apis.task.tasks.TaskRoute.get_task')
def test_get_failed_task(mock_get_task, test_client):
    mock_get_task.return_value = MockTask(C.FAILURE)
    id = 'abcd-3456'

    response = test_client.get(f'/tasks/{id}')
    mock_get_task.assert_called_once_with(id)

    assert response.status_code == 200

    payload = json.loads(response.data)
    assert payload['message'] == (C.CELERY_TASK_FETCHED % id)
    assert payload['status'] == C.FAILURE
    assert payload['result'] == None

@patch('apis.task.tasks.TaskRoute.get_task')
def test_get_non_existant_task(mock_get_task, test_client):
    # doesn't matter what kind of error, any will do
    mock_get_task.side_effect = Exception('foo', 'bar')
    id = 'abcd-4567'

    response = test_client.get(f'/tasks/{id}')
    mock_get_task.assert_called_once_with(id)

    assert response.status_code == 404

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
    assert has_stake(user)
    stake = call(parameterizer.get_stake())

    # Approve the market token allowance
    old_mkt_allowance = call(market_token.allowance(user, voting.address))
    assert old_mkt_allowance == 0
    tx = transact(market_token.approve(voting.address, w3.toWei(10, 'milliether'), opts={'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    assert rct['status'] == 1
    new_mkt_allowance = call(market_token.allowance(user, voting.address))
    assert new_mkt_allowance == w3.toWei(10, 'milliether')
    assert stake <= new_mkt_allowance

# before we can test posting tasks we need to register a datatrust
def test_register_and_confirm(w3, market_token, voting, parameterizer_opts, datatrust):
    user = w3.eth.defaultAccount

    tx = transact(datatrust.register(current_app.config['DNS_NAME'], {'from': user, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    rct = w3.eth.waitForTransactionReceipt(tx)

    reg_hash = w3.keccak(text=current_app.config['DNS_NAME'])

    # should see the candidate now
    is_candidate = call(voting.is_candidate(reg_hash))
    assert is_candidate == True

    # we'll use acct 2 as voter, will likely need market token...
    voter = w3.eth.accounts[2]
    stake = parameterizer_opts['stake']
    trans_rct = maybe_transfer_market_token(w3, market_token, voter, stake)
    # will likely need to approve voting
    app_rct = maybe_increase_market_token_allowance(w3, market_token, voter, voting.address, stake)
    # should be able to vote now
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

@patch('apis.task.tasks.NewTaskRoute.start_task')
def test_post_new_task(mock_start_task, test_client):
    return_value = 'abc-123'
    mock_start_task.return_value = return_value

    response = test_client.post('/tasks/', json={'tx_hash':'0xwhatever'})

    mock_start_task.assert_called_once_with('0xwhatever')
    assert response.status_code == 201
    payload = json.loads(response.data)
    assert payload['message'] == (C.CELERY_TASK_CREATED % return_value)
    assert payload['task_id'] == return_value
