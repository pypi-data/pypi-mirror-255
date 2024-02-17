# setup.py
from setuptools import setup, find_packages

setup(
    name='embloy_sdk',
    version='0.3.1b',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='Carlo Bortolan',
    author_email='carlobortolan@gmail.com',
    description='Embloy\'s SDK for Python',
    long_description=' Embloy\'s Python SDK for interacting with your Embloy integration.',
    long_description_content_type='text/markdown',
    url='https://github.com/embloy/embloy-python',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
    ],
)