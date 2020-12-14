"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


setup(
    name='soothingbot',
    version='0.1.0.dev0',
    description='Telegram bot pretending to be an automaton.',
    packages=find_packages(),
    install_requires=['aiohttp==3.7.3','outhouse==0.1.0'],
)