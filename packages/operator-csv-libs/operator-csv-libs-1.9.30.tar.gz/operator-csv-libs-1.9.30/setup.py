from setuptools import setup, find_packages

setup(
    name='operator-csv-libs',
    version='1.9.30',
    description='Code to manage OLM related CSVs and channels',
    author='bennett-white',
    url='https://github.com/multicloud-ops/operator-csv-libs',
    packages=['operator_csv_libs'],
    install_requires=[
        'requests==2.28.1',
        'pyyaml==6.0.1',
        'pygithub==1.55',
        'dohq-artifactory==0.8.4',
        'natsort==8.3.1'
    ]
)
