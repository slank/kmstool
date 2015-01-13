import os
from kmstool import VERSION
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="kmstool",
    version=VERSION,
    author="Matthew Wedgwood",
    author_email="mwedgwood@gmail.com",
    description=("A tool for storing and retrieving encrypted data using the "
                 "AWS Key Management Service"),
    license="MIT",
    keywords=["amazon", "aws", "kms", "encryption", "key", "management"],
    url = "http://github.com/slank/kmstool",
    packages=['kmstool'],
    long_description=read('README.md'),
    install_requires=[
        'botocore>=0.80.0',
        'pycrypto>=2.6.1',
    ],
    entry_points={
        'console_scripts': [
            'kmstool=kmstool.cli:cli',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
