import os
import random
import struct
import tarfile
from .kms import (
    create_data_key,
    decrypt_data,
)
from tempfile import mkdtemp
from shutil import rmtree
from Crypto.Cipher import AES

CHUNKSIZE = 64 * 1024
ENCKEY_NAME = 'kmstool_key.enc'
PAYLOAD_NAME = 'kmstool_payload'


class FileFormatError(Exception):
    pass


class WorkContext(object):
    def __init__(self):
        self.tmpdir = mkdtemp()
        self.enc_keyfile = os.path.join(self.tmpdir, ENCKEY_NAME)
        self.enc_payload = os.path.join(self.tmpdir, PAYLOAD_NAME)
        self.payload = os.path.join(self.tmpdir, 'payload.tar.gz')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        rmtree(self.tmpdir)

    def encrypt_payload(self, key, source_path, chunksize=CHUNKSIZE):
        archive = tarfile.open(self.payload, mode='w:gz')
        archive.add(source_path, arcname=os.path.basename(source_path))
        archive.close()

        iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        origsize = os.path.getsize(self.payload)

        with open(self.payload, 'rb') as infile:
            with open(self.enc_payload, 'wb') as outfile:
                outfile.write(iv)

                # store the file size with the encrypted data
                outfile.write(encryptor.encrypt(struct.pack('<QQ', origsize, 0)))
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += ' ' * (16 - len(chunk) % 16)

                    outfile.write(encryptor.encrypt(chunk))

    def decrypt_payload(self, key, dest_path, chunksize=CHUNKSIZE):
        with open(self.enc_payload, 'rb') as infile:
            iv = infile.read(16)
            decryptor = AES.new(key, AES.MODE_CBC, iv)

            origsize = 0
            with open(self.payload, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    plaintext = decryptor.decrypt(chunk)
                    if origsize:
                        outfile.write(plaintext)
                    else:
                        origsize, pad = struct.unpack('<QQ', plaintext[0:16])
                        outfile.write(plaintext[16:])

                outfile.truncate(origsize)

            archive = tarfile.open(self.payload)
            archive.extractall(dest_path)
            archive.close()


def pack(kms_client, key_id, input_path, output_path, context=None, chunksize=CHUNKSIZE):
    key, enc_key = create_data_key(kms_client, key_id, context=context)

    archive = tarfile.open(output_path, mode='w:gz')

    with WorkContext() as c:
        with open(c.enc_keyfile, 'w') as f:
            f.write(enc_key)
        c.encrypt_payload(key, input_path, chunksize)
        archive.add(c.enc_keyfile, arcname=ENCKEY_NAME)
        archive.add(c.enc_payload, arcname=PAYLOAD_NAME)

    archive.close()


def unpack(kms_client, input_path, output_path, context=None,
           chunksize=CHUNKSIZE):
    archive = tarfile.open(input_path)
    contents = archive.getnames()
    if ENCKEY_NAME not in contents or PAYLOAD_NAME not in contents:
        raise FileFormatError("{} is not a kmstool archive".format(input_path))

    with WorkContext() as c:
        archive.extract(ENCKEY_NAME, c.tmpdir)
        archive.extract(PAYLOAD_NAME, c.tmpdir)
        with open(c.enc_keyfile) as keyfile:
            key = decrypt_data(kms_client, keyfile.read(), context)
        c.decrypt_payload(key, output_path, chunksize)
