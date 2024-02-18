from setuptools import setup

setup(
    name='salure_helpers_sap',
    version='1.5.6',
    description='SAP wrapper from Salure',
    long_description='SAP wrapper from Salure',
    author='D&A Salure',
    author_email='support@salureconnnect.com',
    packages=["salure_helpers.sap"],
    license='Salure License',
    install_requires=[
        'salure-helpers-salureconnect>=1',
        'requests>=2,<=3',
        'requests_oauthlib>=1,<=2',
        'oauthlib>=3,<=4',
        'pandas_read_xml>=0,<1',
        'pandas>=1,<=2'
    ],
    zip_safe=False,
)
