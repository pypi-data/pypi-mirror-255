from setuptools import setup, find_packages

setup(name='aaaawslogger', 
      version='0.0.2.1', 
      author='ace',
      author_email='kardaras.george@clublabs.com',
      description='Logger',
      packages=find_packages(),
      install_requires=[
          'boto3',
                        ],
      )