__author__ = 'Asier Pereiro Castro'
__email__ = 'asier.pereiro.castro@cern.ch'
__license__ = 'MIT License Copyright (c) 2023 Asier Pereiro Castro'

from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', 'r') as f:
    long_description = f.read().strip()

with open('plottergeist/VERSION.txt') as f:
    version = f.read().strip()

setup(
    name='plottergeist',
    author=__author__,
    author_email=__email__,
    url='https://github.com/apereiroc/plottergeist',
    version=version,
    description='Statistics and scientific plotting',
    download_url='https://github.com/apereiroc/plottergeist.git',
    license='MIT',
    packages=['plottergeist'],
    python_requires=">=3.7",
    include_package_data=True,
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type='text/markdown',
)
