from setuptools import setup, find_packages

install_requires = ['numpy', 'matplotlib', 'orjson', 'jinja2']

setup(name='ta',
      version='0.0.1',
      packages=find_packages(include=['ta*']),
      install_requires=install_requires)