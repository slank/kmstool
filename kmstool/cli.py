import sys
import clip
from .kms import get_client
from .file import (
    store_file,
    retrieve_file,
)

app = clip.App()


def parse_kv(kv_string):
    values = {}
    for kv in kv_string.split(','):
        pair = kv.split('=')
        values[pair[0]] = pair[1]
    return values

standard_args = ['source_path', 'dest_path', '--profile', '--region', '-c']


@app.main(description='A tool for encrypting and decrypting data with the AWS KMS')
@clip.arg('source_path', inherit_only=True)
@clip.arg('dest_path', inherit_only=True)
@clip.opt('--profile', help='AWS client profile name', inherit_only=True)
@clip.opt('--region', help='AWS client region name', inherit_only=True)
@clip.opt('-c', '--encryption-context', help='key=value,key=value', inherit_only=True)
def kmstool():
    pass


@kmstool.subcommand(description='Store KMS-encrypted data', inherits=standard_args)
@clip.arg('key_id', required=True)
def store(key_id, encryption_context, source_path, dest_path, profile, region):
    kms_client = get_client(profile=profile, region=region)
    context = None
    if encryption_context:
        context = parse_kv(encryption_context)
    store_file(kms_client, key_id, source_path, dest_path, context)


@kmstool.subcommand(description='Retrieve KMS-encrypted data', inherits=standard_args)
def retrieve(encryption_context, source_path, dest_path, profile, region):
    kms_client = get_client(profile=profile, region=region)
    context = None
    if encryption_context:
        context = parse_kv(encryption_context)
    retrieve_file(kms_client, source_path, dest_path, context)


def cli():
    try:
        app.run(sys.argv[1:] or '-h')
    except clip.ClipExit:
        pass

if __name__ == '__main__':
    cli()
