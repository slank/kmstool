'''A tool for encrypting and decrypting data with the AWS KMS'''

import os
from argparse import ArgumentParser
from .kms import get_client
from .file import (
    store_file,
    retrieve_file,
)


def parse_kv(kv_string):
    values = {}
    for kv in kv_string.split(','):
        pair = kv.split('=')
        values[pair[0]] = pair[1]
    return values


def store(args):
    kms_client = get_client(profile=args.profile, region=args.region)
    context = None
    if args.encryption_context:
        context = parse_kv(args.encryption_context)
    store_file(kms_client, args.key_id, args.source_path, args.dest_path, context)


def retrieve(args):
    kms_client = get_client(profile=args.profile, region=args.region)
    context = None
    if args.encryption_context:
        context = parse_kv(args.encryption_context)
    retrieve_file(kms_client, args.source_path, args.dest_path, context)


def cli():
    common_args = ArgumentParser(add_help=False, description=__doc__)
    common_args.add_argument('--profile', help='AWS client profile')
    common_args.add_argument('--region', help='AWS region')
    common_args.add_argument('-c', '--encryption-context',
                             help='key=val,key=val')
    common_args.add_argument('source_path')
    common_args.add_argument('dest_path')

    ap = ArgumentParser()
    sp = ap.add_subparsers()

    store_ap = sp.add_parser('store', help='Store KMS-encrypted data',
                             parents=(common_args,))
    store_ap.add_argument('key_id')
    store_ap.set_defaults(func=store)

    retr_ap = sp.add_parser('retrieve', help='Retrieve KMS-encrypted data',
                            parents=(common_args,))
    retr_ap.set_defaults(func=retrieve)

    args = ap.parse_args()
    if not os.path.exists(args.source_path):
        ap.exit(1, 'File not found: {}\n'.format(args.source_path))
    if os.path.isdir(args.source_path):
        ap.exit(1, 'Cannot yet operate on directories\n')

    args.func(args)

if __name__ == '__main__':
    cli()
