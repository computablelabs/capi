from flask import current_app
import pytest
from core.constants import REGISTERED_CANDIDATE
from computable.helpers.transaction import call

def test_register(voting, datatrust, ctx):
    runner = current_app.test_cli_runner()
    result = runner.invoke(args=['admin', 'registration_test'])
    # TODO: The swap to staked registration means that registering with the register CLI command fails without CMT for staking. Fix the registration test to stake properly so the registered candidate is actually in output
    assert REGISTERED_CANDIDATE not in result.output

def test_registered_candidate(w3, voting, ctx):
    hash = w3.keccak(text=current_app.config['DNS_NAME'])
    candidate = call(voting.is_candidate(hash))
    # TODO:This should be fixed so the candidate is actually made once registration test above is fixed
    assert candidate == False 
