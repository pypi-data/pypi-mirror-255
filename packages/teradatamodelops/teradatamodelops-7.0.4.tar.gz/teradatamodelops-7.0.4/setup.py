from setuptools import setup, find_packages
from aoa import __version__

NAME = "teradatamodelops"

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("docs/pypi.md", "r") as fh:
    long_description = fh.read()

setup(
    name=NAME,
    version=__version__,
    description="Python client for Teradata ModelOps (TMO)",
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    license_files=['LICENSE.txt', 'LICENSE-3RD-PARTY.txt'],
    author="Teradata",
    author_email="teradata.corporation@teradatacorporation.com",
    url="",
    install_requires=required,
    tests_require=['pytest', 'pytest-console-scripts'],
    setup_requires=['pytest-runner'],
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    scripts=['scripts/aoa','scripts/tmo']
)
