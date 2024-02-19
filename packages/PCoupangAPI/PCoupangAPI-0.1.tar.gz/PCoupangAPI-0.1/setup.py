from setuptools import setup, find_packages

setup(
    name='PCoupangAPI',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='raykim',
    author_email='ray@jejememe.com',
    description='A Python wrapper for the Coupang partner API',
    keywords='coupang partner api wrapper',
    url='https://github.com/JEJEMEME/PCoupangAPI',
)
