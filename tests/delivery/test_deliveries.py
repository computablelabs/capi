import pytest

def test_jwt_required(test_client):
    delivery = test_client.get('/deliveries/')
    assert delivery.status_code == 401
