from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
  
setup(
    name='clone_search_abs',
    version='0.21',
    packages=find_packages(),
    install_requires=requirements,
)
