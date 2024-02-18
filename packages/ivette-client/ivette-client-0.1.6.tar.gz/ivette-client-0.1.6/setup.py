from setuptools import setup
import json

with open('config.json') as f:
    setup_args = json.load(f)

setup(
    include_package_data=True,
    **setup_args
)
