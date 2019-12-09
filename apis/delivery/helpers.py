from flask import current_app, g
from core.protocol import get_datatrust
from core.helpers import metrics_collector, send_or_transact, set_gas_prices
from computable.helpers.transaction import call


@metrics_collector
def get_delivery(delivery_hash):
    """
    Returns owner, bytes_requested, and bytes_delivered for a delivery
    """
    d = get_datatrust()
    return call(d.get_delivery(delivery_hash))


@metrics_collector
def listing_accessed(delivery_hash, listing, amount, gas_price):
    """
    Commit to protocol the listing accessed details
    """
    d = get_datatrust()
    # we must set the gas prices appropriately
    t = d.listing_accessed(listing, delivery_hash, amount)
    args = set_gas_prices(t, gas_price)
    tx = send_or_transact(args)
    # do not block here so just return the unmined tx
    return tx


@metrics_collector
def delivered(delivery_hash, url, gas_price):
    """
    Mark the delivery as complete in protocol
    """
    d = get_datatrust()
    t = d.delivered(delivery_hash, url)
    args = set_gas_prices(t, gas_price)
    tx = send_or_transact(args)
    # do not block, simply return the unmined tx
    return tx


def get_deliveries(delivery_hash, owner):
    """
    Given a specific delivery and an owner, search back to our
    GENESIS_BLOCK, returning any matching events
    """
    d = get_datatrust()

    from_block = current_app.config['GENESIS_BLOCK']
    is_str = isinstance(delivery_hash, str)
    hash = g.w3.toBytes(hexstr=delivery_hash) if is_str else g.w3.toBytes(delivery_hash)
    arg_filters = dict(hash=hash, owner=owner)

    filter = d.deployed.events.Delivered.createFilter(
        fromBlock=from_block, argument_filters=arg_filters)

    return filter.get_all_entries()


def was_delivered(delivery_hash, owner):
    entries = get_deliveries(delivery_hash, owner)
    return len(entries) > 0
