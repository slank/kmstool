'''A tool for encrypting and decrypting data with the AWS KMS'''

import os
from argparse import ArgumentParser
from .kms import get_client
from . import files


def parse_kv(kv_string):
    values = {}
    for kv in kv_string.split(','):
        pair = kv.split('=')
        values[pair[0]] = pair[1]
    return values


def pack(args):
    kms_client = get_client(profile=args.profile, region=args.region)
    context = None
    if args.encryption_context:
        context = parse_kv(args.encryption_context)
    files.pack(kms_client, args.key_id,
               args.source_path, args.source_path + '.kt', context)


def unpack(args):
    kms_client = get_client(profile=args.profile, region=args.region)
    context = None
    if args.encryption_context:
        context = parse_kv(args.encryption_context)
    files.unpack(kms_client, args.source_path, '.', context)


def cli():
    common_args = ArgumentParser(add_help=False, description=__doc__)
    common_args.add_argument('--profile', help='AWS client profile')
    common_args.add_argument('--region', help='AWS region')
    common_args.add_argument('-c', '--encryption-context',
                             help='key=val,key=val')

    ap = ArgumentParser()
    sp = ap.add_subparsers()

    pack_ap = sp.add_parser('pack', help='Store KMS-encrypted data',
                            parents=(common_args,))
    pack_ap.add_argument('key_id')
    pack_ap.add_argument('source_path')
    pack_ap.set_defaults(func=pack)

    unpack_ap = sp.add_parser('unpack', help='Retrieve KMS-encrypted data',
                              parents=(common_args,))
    unpack_ap.add_argument('source_path')
    unpack_ap.set_defaults(func=unpack)

    args = ap.parse_args()
    if not os.path.exists(args.source_path):
        ap.exit(1, 'File not found: {}\n'.format(args.source_path))
    if args.source_path.endswith("/"):
        args.source_path = args.source_path[:-1]

    args.func(args)

if __name__ == '__main__':
    cli()
