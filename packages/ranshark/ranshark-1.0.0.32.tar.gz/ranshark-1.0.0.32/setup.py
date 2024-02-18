from setuptools import setup,find_packages
from distutils.core import setup
from pathlib import Path
import os

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='ranshark',
    version='1.0.0.32',
    description='A friendly 4G-LTE/5G o-ran packet analyzing tool with GUI interface.',
    license="Apache-2.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='ugandhar',
    author_email='ugandhar.nellore@gmail.com',
    keywords=['ran', '5g','lte', '5g analyzer', 'ranshark','4g'],

    classifiers=[
        "Intended Audience :: Telecommunications Industry",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.10",
    ],

        install_requires=[
        'Django',
        'pandas==2.1.4',
        'pyshark==0.6',
        'psycopg2',
        'psycopg2-binary',
        'numpy==1.26.2',
        'importlib',
        'openpyxl',
    ],
    include_package_data = True,
    package_data={'drawranflow': ['migrations/__init__.py']},

    )
