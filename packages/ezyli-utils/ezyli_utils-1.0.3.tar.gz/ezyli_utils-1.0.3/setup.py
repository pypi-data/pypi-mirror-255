from setuptools import setup, find_packages

setup(
    name='ezyli_utils',
    version='1.0.3',
    packages=find_packages(),
    install_requires=[
        'pika==1.3.2',
        'jsonschema==4.20.0'
    ],
)