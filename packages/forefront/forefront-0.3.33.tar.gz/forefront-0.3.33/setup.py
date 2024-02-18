from setuptools import setup, find_packages

setup(
    name='forefront',
    version='0.3.33',
    packages=find_packages(),
    install_requires=[
        'requests',
        'aiohttp',
        'asyncio',
    ],
)
