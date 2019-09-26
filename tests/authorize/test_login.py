from datetime import datetime, timedelta
import pytest
import json
from flask import current_app, g
from flask_jwt_extended import decode_token
from freezegun import freeze_time
from core import constants as C

def test_valid_login(test_client):
    login = test_client.post('/authorize/', json={
        'public_key': 'asdf',
        'message': 'message'
    })
    payload = json.loads(login.data)
    assert login.status_code == 200

    assert payload['message'] == C.LOGIN_SUCCESS
    assert payload['jwt'] is not None

    claims = decode_token(payload['jwt'])
    assert claims['identity'] == 'asdf'

    expiration = datetime.now() + timedelta(days=current_app.config['EXPIRES_IN_DAYS'])
    assert claims['exp'] <= expiration.timestamp() 

def test_no_login_payload(test_client):
    login = test_client.post('/authorize/')
    assert login.status_code == 400

def test_expired_token(test_client):
    login = test_client.post('/authorize/', json={
        'public_key': 'asdf',
        'message': 'message'
    })
    payload = json.loads(login.data)
    expired = datetime.now() + timedelta(days=current_app.config['EXPIRES_IN_DAYS']+30)
    with freeze_time(expired):
        headers = {
            'Authorization': 'Bearer {}'.format(payload['jwt'])
        }
        delivery = test_client.get('/deliveries/', headers=headers)
        assert delivery.status_code == 401
