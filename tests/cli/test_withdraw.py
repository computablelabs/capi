import pytest
from flask import current_app
from core.constants import WITHDRAWN

def test_withdraw(voting, reserve, ctx):
    runner = current_app.test_cli_runner()
    result = runner.invoke(args=['admin', 'withdraw_test'])
    print("TEST_WITHDRAW ----------------------------------------------------------------")
    print(result)
    assert WITHDRAWN in result.output

