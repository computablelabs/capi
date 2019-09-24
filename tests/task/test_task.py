import json
import pytest
from unittest.mock import patch
import core.constants as C

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
