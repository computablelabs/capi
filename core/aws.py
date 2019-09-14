import json
import boto3
from botocore.exceptions import ClientError
from app import app
import logging

logging.config.fileConfig('logging.config')
log = logging.getLogger()
log.setLevel(app.config['LOG_LEVEL'])

def get_secrets(env, region):
    secret_name = f'ffa/datatrust/{env}'
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region)

    try:
        log.debug('Getting secrets from AWS')
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        log.critical(f'Error retrieving secrets from AWS: {e.response["Error"]["Code"]}')
        raise e
    else:
        return json.loads(response['SecretString'])
