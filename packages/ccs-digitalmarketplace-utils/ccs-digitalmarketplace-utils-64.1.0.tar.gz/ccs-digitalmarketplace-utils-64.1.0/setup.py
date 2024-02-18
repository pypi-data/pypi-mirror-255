"""
Common utils for Digital Marketplace apps.
"""
import re
import ast
from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('dmutils/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='ccs-digitalmarketplace-utils',
    version=version,
    url='https://github.com/Brickendon-DMp1-5/digitalmarketplace-utils',
    license='MIT',
    author='GDS Developers',
    description='Common utils for Digital Marketplace apps.',
    long_description=__doc__,
    packages=find_packages(),
    package_data={'dmutils': ['py.typed']},
    include_package_data=True,
    install_requires=[
        'Flask-WTF>=1.2.1',
        'Flask>=1.0,<2.1',
        'Flask-gzip>=0.2',
        'Flask-Login>=0.6.2',
        'Flask-Session<0.5.0,>=0.4.1',
        'markupsafe<=2.0.1',
        'boto3<2,>=1.7.83',
        'contextlib2>=21.6.0',
        'cryptography>=41.0.4',
        'ccs-digitalmarketplace-apiclient>=25.0.0',
        'govuk-country-register>=0.5.0',
        'mailchimp3==3.0.21',
        'requests>=2.22.0,<3',
        'redis>=5.0.1',
        'fleep<1.1,>=1.0.1',
        'notifications-python-client>=8.1.0,<9.0.0',
        'odfpy>=1.4.1',
        'python-json-logger>=2.0.7,<3.0.0',
        'pytz',
        'unicodecsv>=0.14.1',
        'workdays>=1.4',
    ],
    python_requires="~=3.9",
)
