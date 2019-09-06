from flask import current_app
import pytest
from core.constants import REGISTERED_CANDIDATE
from computable.helpers.transaction import call

def test_register(voting, datatrust, ctx):
    runner = current_app.test_cli_runner()
    result = runner.invoke(args=['admin', 'registration_test'])
    assert REGISTERED_CANDIDATE in result.output

def test_registered_candidate(w3, voting, ctx):
    hash = w3.keccak(text=current_app.config['DNS_NAME'])
    candidate = call(voting.is_candidate(hash))
    assert candidate == True
