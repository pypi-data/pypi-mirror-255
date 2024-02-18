import os
from setuptools import setup, find_packages, find_namespace_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='aaaawslogger', 
      version='0.0.2.6', 
      author='ace',
      author_email='kardaras.george@clublabs.com',
      description='Logger',
      packages=['aws_logger_project'],
      long_description=read('README.md'),
      #package_dir={'': 'src'},
      #packages=find_packages(),
      install_requires=[
          'boto3',
                        ],
      )