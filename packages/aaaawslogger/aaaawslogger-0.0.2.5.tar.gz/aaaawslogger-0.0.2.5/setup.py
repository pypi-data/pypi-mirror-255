from setuptools import setup, find_packages, find_namespace_packages

setup(name='aaaawslogger', 
      version='0.0.2.5', 
      author='ace',
      author_email='kardaras.george@clublabs.com',
      description='Logger',

      package_dir={'': 'src'},
      packages=find_namespace_packages(where='src'),
      #packages=find_packages(),
      install_requires=[
          'boto3',
                        ],
      )