import botocore.session
from botocore.exceptions import ClientError
from urllib2 import urlopen, URLError

AWS_MD_AZ_URL = 'http://169.254.169.254/latest/meta-data/placement/availability-zone'


class EncryptionError(Exception):
    pass


def discover_region():
    try:
        response = urlopen(AWS_MD_AZ_URL, timeout=1)
        return response.read()[:-1]
    except URLError:
        return None


def get_client(region=None, profile=None):
    session = botocore.session.get_session()
    region = region or discover_region()

    if not region:
        raise ValueError('Region was not provided and could not be determined')

    session.set_config_variable('region', region)
    if profile:
        session.set_config_variable('profile', profile)

    return session.create_client('kms', region_name=region)


def create_data_key(client, key_id, context=None, keyspec='AES_256'):
    '''
    Create a KMS data key. Returns the plaintext key to be used for encryption
    as well as the KMS-encrypted version of the key to be stored with the
    encrypted data.
    '''
    args = {
        'KeyId': key_id,
        'KeySpec': keyspec,
    }
    if context:
        args['EncryptionContext'] = context

    response = client.generate_data_key(**args)
    # return (b64decode(response['Plaintext']), response['CiphertextBlob'])
    return (response['Plaintext'], response['CiphertextBlob'])


def decrypt_data(client, ciphertext, context=None):
    '''
    Decrypt a cyphertext using KMS. Returns the plaintext version of the
    given data.
    '''
    args = {
        'CiphertextBlob': ciphertext,
    }
    if context:
        args['EncryptionContext'] = context

    try:
        return client.decrypt(**args)['Plaintext']
    except ClientError as e:
        raise EncryptionError('Encryption failed: ' + str(e))


def alias_to_id(client, key_alias):
    '''
    Look up a key ID from a key alias.
    '''
    response = client.list_aliases()
    if response and 'Aliases' in response:
        for alias in response['Aliases']:
            if alias['AliasName'] == key_alias:
                return alias.get('TargetKeyId', None)
    return None
