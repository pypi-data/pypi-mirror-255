from setuptools import setup
setup(name="encrypter2",
version="1.1.0",
description="This is an encoder package",
long_description="This is python package helps us encode a given text using some basic encryption algorithms after this release we can import using ```import encrypter2``` in place of ```import encoder```",
author="Kanishk",
packages=["encrypter2"],
install_requires=["nltk"]
)