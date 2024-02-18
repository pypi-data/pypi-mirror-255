import os
from setuptools import setup, find_packages, find_namespace_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='aceagentaws', 
      version='0.0.1', 
      author='ace',
      author_email='kardaras.george@clublabs.com',
      description='Logger',
      long_description=read('README.md'),
      packages=find_namespace_packages(),

      install_requires=[
          'boto3',
          'aceagentaws>=0.0.1',
                        ],
      )