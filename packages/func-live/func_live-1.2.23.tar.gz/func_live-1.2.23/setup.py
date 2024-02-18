from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='func_live',
    version='1.2.23',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'requests',
        'httpx'
    ],
    description="Allows you to import and call the functions on www.func.live",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Aravind Vakil",
    license="ISC",
    keywords="func.live func functions",
    url="https://func.live"
)
