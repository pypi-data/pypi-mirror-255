from knowl_apidocs.version import VERSION
from setuptools import setup

NAME = "knowl_apidocs"
VERSION = "".join([char for char in VERSION if not char.isspace()])
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name=NAME,
    version=VERSION,
    url="https://github.com/knowl-doc/APIDocs",
    entry_points={"console_scripts": ["knowl_apidocs = knowl_apidocs.apidocs:main", "knowl-apidocs = knowl_apidocs.apidocs:main"]},
    long_description=long_description,
    long_description_content_type='text/markdown',
)
