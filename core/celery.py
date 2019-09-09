"""
Abstractions for celery and asynchronous tasks handled by celery workers
"""
import celery
from flask import current_app, g
from core.protocol import get_datatrust, is_registered
from computable.helpers.transaction import call, transact, send

def set_celery(clry=None):
    """
    Configure celery and push onto the global context
    """
    if 'celery' not in g:
        if clry == None:
            clry = celery.Celery(
                current_app.config['PUBLIC_KEY'],
                broker=current_app.config['CELERY_BROKER_URL']
            )
        g.celery = clry

@celery.task
def send_hash_after_mining(listing, data_hash):
    """
    Wait for the transaction to be mined, then set the data_hash
    for the uploaded file in protocol
    """
    #TODO: calculate hash for listing
    #TODO: wait for transaction to be mined
    #TODO: set the data hash
    if is_registered == True:
        dt = get_datatrust()
        t = dt.set_data_hash(listing, data_hash)
        # TEST env never need use send...
        if current_app.config['TESTING'] == True:
            tx = transact(t)
        else:
            tx = send(g.w3, current_app.config['PRIVATE_KEY'], t)