from setuptools import setup, find_packages

VERSION = '0.0.22'
name = 'spider_toolbox'
author = 'neco_arc'
description = '爬虫工具库'
email = '3306601284@qq.com'

with open('README.md', mode='r', encoding='utf-8') as f:
    long_description = f.read()
setup(
    name=name,
    version=VERSION,
    author=author,
    author_email=email,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sweetnotice/spider_toolbox',
    package_dir={'spider_toolbox': 'src'},
    packages=['spider_toolbox'],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'PyExecJS',
        'rich',
        'pycryptodome'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
