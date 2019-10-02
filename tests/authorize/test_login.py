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
    assert payload['access_token'] is not None
    assert payload['refresh_token'] is not None

    claims = decode_token(payload['access_token'])
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
    expired = datetime.now() + timedelta(days=current_app.config['EXPIRES_IN_DAYS']+1)
    with freeze_time(expired):
        headers = {
            'Authorization': f'Bearer {payload["access_token"]}'
        }
        delivery = test_client.get('/deliveries/', headers=headers)
        # Verify that access was denied due to expired token
        assert delivery.status_code == 401

        # Verify the refresh token can be exchanged for a new valid token
        refresh_header = {
            'Authorization': f'Bearer {payload["refresh_token"]}'
        }
        refresh = test_client.get(
            '/authorize/', 
            query_string={'refresh': True},
            headers=refresh_header
        )
        new_tokens = json.loads(refresh.data)
        assert new_tokens['access_token'] is not None
        assert new_tokens['refresh_token'] is not None

        # Assert the client can access a protected endpoint with the new token
        headers = {
            'Authorization': f'Bearer {new_tokens["access_token"]}'
        }
        delivery = test_client.get('/deliveries/', headers=headers)
        assert delivery.status_code == 200