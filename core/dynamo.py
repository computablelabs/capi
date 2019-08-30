"""
Abstractions for our instance of a dynamo db table that lives in the global context for each request.
NOTE: It is assumed that this table is pre-made and the table name (and url) are set in the current_app
config object at initialization (with test handled via conftest)
"""
import os
from flask import current_app, g
import boto3
# from botocore.exceptions import ClientError

def set_dynamo_table(db=None):
    """
    place a dynamo table in the global env for this request
    NOTE: test env will pass a mocked dynamo
    """
    if 'table' not in g: # check is here as test env will stub before the request cycle begins
        if db == None:
            db = boto3.resource('dynamodb', current_app.config['REGION'], endpoint_url=current_app.config['DB_URL'])

        g.table = db.Table(current_app.config['TABLE_NAME'])

def get_listings():
    """
    Fetch and return all DB listings
    :return: dict
    TODO: paging? offsets? can we use a list of hashes to filter?
    """
    response = g.table.scan()
    if 'Items' in response: # stupid fukin capital i...
        return response['Items']
    else:
        return {}
