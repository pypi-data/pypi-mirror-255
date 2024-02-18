import os, sys
from setuptools import setup
from setuptools import find_packages
from sling import cli

version = cli('--version', return_output=True).strip().replace('Version: ', '')

if not version:
  raise Exception('version is blank')
elif version == 'dev':
  version='v0.0.dev'

setup(
  name='sling',
  version=version,
  description='Slings data from a source to a target',
  author='Fritz Larco',
  author_email='fritz@slingdata.io',
  url='https://github.com/slingdata-io/sling-python',
  download_url='https://github.com/slingdata-io/sling-python/archive/master.zip',
  keywords=['sling', 'etl', 'elt', 'extract', 'load'],
  packages=find_packages(exclude=['tests']),
  long_description_content_type='text/markdown',
  long_description=open(os.path.join(os.path.dirname(__file__),
                                     'README.md')).read(),
  include_package_data=True,
  install_requires=[],
  extras_require={},
  entry_points={
    'console_scripts': ['sling=sling:cli',],
  },
  classifiers=[
    'Programming Language :: Python :: 3', 'Intended Audience :: Developers',
    'Intended Audience :: Education', 'Intended Audience :: Science/Research',
    'Operating System :: MacOS', 'Operating System :: Unix',
    'Topic :: Utilities'
  ])
