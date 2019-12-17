import json
import pytest

def test_get_consent(w3, test_client, mocked_cloudwatch):
    consent = test_client.get(f'/consent/?owner={w3.eth.accounts[1]}')
    payload = json.loads(consent.data)

    assert payload['timestamp'] == 12345
    assert payload['from_us'] == True
    assert payload['version'] == 1
