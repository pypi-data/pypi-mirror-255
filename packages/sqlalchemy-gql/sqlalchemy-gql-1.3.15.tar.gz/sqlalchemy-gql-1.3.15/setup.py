import io

from setuptools import setup, find_packages

with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('VERSION') as version_file:
    version = version_file.read().strip().lower()
    if version.startswith("v"):
        version = version[1:]

setup(
    name='sqlalchemy-gql',
    version=version,
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    author='Robert Parker',
    author_email='rob@parob.com',
    url='https://gitlab.com/parob/sqlalchemy-gql',
    download_url=f'https://gitlab.com/parob/sqlalchemy-gql/-/archive/'
                 f'v{version}/sqlalchemy-gql-v{version}.tar.gz',
    description='Map SQLAlchemy models to GraphQL Objects.',
    keywords=['GraphQL', 'GraphQL API', 'Server', 'DataRM', 'ORM'],
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=[
        "graphql-core>=3.0.0",
        "sqlalchemy>=1.4.0",
        "sqlalchemy-utils>=0.40.0",
        "graphql-api>=1.0.2",
        "context-helper>=1.0.1"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
