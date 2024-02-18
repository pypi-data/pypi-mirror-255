# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='hews',
    version='0.0.3',
    packages=find_packages(),
    long_description=open('README.txt').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        "hehd==1.0.0",
        "heuf==1.0.0",
        "Flask==3.0.2",
        "colorama==0.4.6"
    ],
    entry_points={
        'console_scripts': [
            'hews = hews.console:run',
        ],
    },
    python_requires='>=3.12',
)
