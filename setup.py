from setuptools import setup, find_packages

install_requires = ['numpy', 'matplotlib', 'orjson', 'jinja2']
extras_require = {'dev': ['ipython', 'sphinx']}

setup(name='AutoSweep',
      version='0.1.0',
      python_requires='>3.10',
      packages=find_packages(include=['autosweep*']),
      install_requires=install_requires,
      extras_require=extras_require)