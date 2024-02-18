from setuptools import setup, find_packages
import json

with open('config.json') as f:
    setup_args = json.load(f)

setup(
    packages=find_packages(),
    package_data={
        '': ['config.json'],  # All packages can access config.json
    },
    include_package_data=True,
    **setup_args
)
