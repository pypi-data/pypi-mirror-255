#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: javiera.quiroz
"""

from setuptools import setup

setup(
    name='D3mel',
    version='0.0.6',
    license='MIT',
    author='Javiera Quiroz Olave',
    url= 'https://github.com/JavieraQuirozO/D3mel',
    author_email='javiera.quiroz@biomedica.udec.cl',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=open('requirements.txt').readlines(),
    description='Data Downloader of Drosophila melanogaster',
    packages=['D3mel','D3mel.utilities', 'D3mel.utilities.ExtraData'],
    package_data={
        'D3mel': ['utilities/ExtraData/7227.tsv'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
