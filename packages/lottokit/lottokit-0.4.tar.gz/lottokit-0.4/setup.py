#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Author  : nickdecodes
@Email   : nickdecodes@163.com
@Usage   :
@FileName: setup.py
@DateTime: 2024/1/28 18:50
@SoftWare: 
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='lottokit',
    version='0.4',
    keywords=['lottokit', 'lottery'],
    packages=find_packages(),
    package_data={"": ["LICENSE", "NOTICE"]},
    include_package_data=True,
    author="nickdecodes",
    author_email="nickdecodes@163.com",
    description="Lotto Kit Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    install_requires=[
        'selenium>=4.11.2',
        'webdriver_manager>=4.0.0',
        'pandas>=2.0.3',
        'numpy>=1.24.3',
        'statsmodels>=0.14.0',
        'Pillow>=9.5.0',
        'scikit-learn>=1.3.2',
        'pmdarima>=2.0.4',
        'requests',
        'twine'
    ],
    project_urls={
        "Documentation": "http://python-lottokit.readthedocs.io",
        "Source": "https://github.com/nickdecodes/python-lottokit",
    },
)
