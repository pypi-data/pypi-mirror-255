# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='hews',
    version='0.0.1',
    packages=find_packages(),
    long_description=open('README.txt').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        "hehd",
        "heuf"
    ],
    entry_points={
        'console_scripts': [
            'hews = hews.console:run',
        ],
    },
    python_requires='>=3.12',
)
