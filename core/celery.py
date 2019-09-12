"""
Abstractions for celery and asynchronous tasks handled by celery workers
"""
from celery import Celery, task, Task
from flask import current_app, g
from .protocol import get_datatrust, is_registered
from .helpers import set_gas_prices
from computable.helpers.transaction import call, transact, send

def make_celery(app):
    """
    celery is setup at the app.py level and not at the request level,
    thus current_app is not appropriate here...
    """
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

@task
def send_hash_after_mining(tx_hash, listing, data_hash):
    """
    Wait for the transaction to be mined, then set the data_hash
    for the uploaded file in protocol
    """
    if is_registered() == True:
        # TODO timeout length?
        tx_rcpt = g.w3.eth.waitForTransactionReceipt(tx_hash)
        dt = get_datatrust()
        # t = dt.set_data_hash(listing, data_hash, {'gas': 1000000, 'gas_price': g.w3.toWei(2, 'gwei')})
        t = dt.set_data_hash(listing, data_hash)
        gwei = 2 # TODO use get_gas_price ethgasstation call
        t = set_gas_prices(t, gwei)
        # TODO send_or_transact
        if current_app.config['TESTING'] == True:
            tx = transact(t)
        else:
            tx = send(g.w3, current_app.config['PRIVATE_KEY'], t)

        # TODO timeout length?
        hash_rcpt = g.w3.eth.waitForTransactionReceipt(tx)
        return hash_rcpt
