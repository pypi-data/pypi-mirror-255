"""
Documentation for setup.py files is at https://setuptools.readthedocs.io/en/latest/setuptools.html
"""

from setuptools import setup, find_namespace_packages

# Import the README.md file contents
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='heaserver',
      version='1.0.6',
      description='The server side of HEA.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://risr.hci.utah.edu',
      author='Research Informatics Shared Resource, Huntsman Cancer Institute, Salt Lake City, UT',
      author_email='Andrew.Post@hci.utah.edu',
      python_requires='>=3.10',
      package_dir={'': 'src'},
      packages=find_namespace_packages(where='src'),
      package_data={'heaserver.service': ['py.typed', 'jsonschemafiles/*']},
      install_requires=[
          'heaobject~=1.0.1',
          'aiohttp[speedups]~=3.8.6',
          'hea-aiohttp-remotes~=1.2.1',  # replace with aiohttp-remotes if they incorporate our patch.
          'motor~=3.2.0',
          'motor-types~=1.0.0b2',
          'accept-types~=0.4.1',
          'mongoquery~=1.4.2',
          'jsonschema~=4.17.3',
          'jsonmerge~=1.9.1',
          'requests>=2.31.0',
          'types-requests>=2.31.0.1',  # Should be set at same version as requests.
          'boto3~=1.28.83',
          'botocore~=1.31.83',
          'boto3-stubs[essential,sts,account,organizations]~=1.28.83',
          'botocore-stubs[essential]~=1.31.83',
          'freezegun~=1.0.0',  # Bug fixed in Feb 2023, awaiting new release. See https://github.com/spulec/freezegun/issues/437
          'regex~=2023.6.3',
          'aio-pika==9.1.4',
          'simpleeval~=0.9.13',
          'cachetools~=5.3.2',
          'types-cachetools~=5.3.0'
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Software Development',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering :: Medical Science Apps.'
      ]
      )
