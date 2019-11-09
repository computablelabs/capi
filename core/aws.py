import json
import boto3
from botocore.exceptions import ClientError

def get_secrets(network, region):
    secret_name = network
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region)

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            raise e
        else:
            # Raise anything we didn't catch
            raise e
    else:
        return json.loads(response['SecretString'])
