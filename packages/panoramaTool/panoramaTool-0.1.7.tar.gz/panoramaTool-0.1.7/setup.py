import os
import re

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
PACKAGE_INIT = os.path.abspath(os.path.join('panoramaTool', '__init__.py'))

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', 'r') as f:
    long_description = f.read()


def find_version(filename):
    """Attempts to find the version number in the file names filename.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(filename, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


__version__ = find_version(PACKAGE_INIT)

setup(
    name='panoramaTool',
    description='This tool is intended to insert sercurity post rules into Panorama via API.',
    version=__version__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Timo Riedinger',
    author_email='timo.riedinger@bechtle.com',
    packages=find_packages(),
    install_requires=requirements,
    package_data={'panoramaTool': ['templates/*.html', 'static/*.css', 'csv/']},
    license='MIT',
    license_files=['LICENSE'],
    classifiers=[
        'Programming Language :: Python :: 3.11'
    ]
)
