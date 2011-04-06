# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='ContextIO Client Library',
    version='1.0',
    author='Julien Grenier',
    author_email='julien.grenier42@gmail.com',
    description='Library for accessing the ContextIO API in Python',
    url='https//github.com/contextio/Python-ContextIO',
    packages=['contextIO','example'],
    license='MIT Licence',
    install_requires = ['oauth2', 'httplib2'],
    keywords=['contextIO', 'dokdok', 'imap', 'oauth']
)