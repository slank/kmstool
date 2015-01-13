# kmstool

kmstool helps you encrypt data using the Amazon Key Management Service in AWS.

## Installing

```
pip install .
```

## Usage

kmstool has two modes: pack and unpack

### store

```
kmstool pack <key_id> <source>
```

This command takes a KMS key ID, produces a data key, and uses that key to
encrypt the file <source>. An encrypted copy of the data key is stored, along
with the encrypted files, in the current directory.

### retrieve

```
kmstool retrieve <source>
```

This command reads the contents of <source> passing the encrypted data key to
KMS, and using the resulting plaintext key to decrypt the original data. The
files are extracted to the current directory.

### Additional Options

Additional options are available: see `kmstool -h` for usage information.

Unless otherwise specified, AWS credentials are determined by first examining
the environment, then a search of the AWS metadata service, and finally using
the "default" botocore profile.

```
--profile
    AWS (botocore) profile to use when contacting the KMS.
--region
    AWS region to connect to for KMS.
```

An optional encryption context may be passed when storing files. The same
context must be passed when retrieving them.

```
-c --encryption-context foo=bar,baz=qux
```

## Internals

The output of `kmstool pack` is a gzipped GNU tar file containing the
KMS-encrypted data key plus an encrypted tar.gz of the source data. The
encrypted data is stored as follows (numbers are byte offsets).

```
0-15 Initialization Vector
16-N Encrypted data:
     0-15 Original filesize
     16-N Original data
```
