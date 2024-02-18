from setuptools import setup, find_packages

setup(
    name='ascend-io-dbt-utils',
    version='0.11.1',
    description='Utilities for dbt and Ascend',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(
        exclude=['tests', 'tests.*'],
        ),
    entry_points='''
        [console_scripts]
        ascend_dbt_utils=packages.cli:cli
    ''',
    install_requires=[
        'ascend-io-sdk==0.2.62',
        'click==8.1.7',
        'python-dotenv==1.0.0',
    ],
    url='https://github.com/michaelhyatt/ascend_dbt_transform'
)