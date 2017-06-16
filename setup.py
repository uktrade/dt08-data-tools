from setuptools import setup, find_packages

requirements = [
    'boto3'
    ]

setup(
    name='uktrade_data_tools',
    version='0.1',
    description='utilities for use in data software',
    url='https://github/uktrade/dt08-data-tools',
    author='Department for International Trade Data Team',
    author_email='cammil.taank@digital.trade.gov.uk',
    classifiers=[
        'Development Status :: 3 - Alpha', 'Intended Audience :: Developers',
        'Topic :: Software Development :: Data Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='data tools utilities data-science',
    install_requires=requirements,
    packages=find_packages(exclude='tests'))
