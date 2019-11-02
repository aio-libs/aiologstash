from setuptools import setup, find_packages

from aiologstash import __version__
import os

installs = []
if os.name == 'nt':
    installs+=['pywin32']

setup(
    name='aiologstash',
    version=__version__,
    packages=find_packages(exclude=[
        'test',
    ]),
    install_requires=installs+[
        'flit==1.3',
        'async-timeout==3.0.1'
    ],
    extras_require={
        'testing': [
        ],
    },
)
