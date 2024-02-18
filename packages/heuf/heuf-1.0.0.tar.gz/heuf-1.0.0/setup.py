# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='heuf',
    version='1.0.0',
    packages=find_packages(),
    long_description=open('README.txt').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        # 添加其他依赖项
    ],
    python_requires='>=3.12',
)
