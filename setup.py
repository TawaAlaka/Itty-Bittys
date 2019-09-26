"""Packaging information for the project.

In order to start development for this project on your system, first make
sure you've created a virtual environment for the project and then run the
command while in the root directory of the project:

$ pip install -e .

This will install all dependencies without modifying or copying the source
code itself. This is different when running without the -e flag:

$ pip install .

This packages the project

"""

from setuptools import setup, find_packages


setup(
    # Name of the project.
    name='diet-journal',

    # We will follow semver versioning for each release. If you're
    # unfamiliar with it you can read more about it here:
    # https://semver.org
    version='0.1.0',

    # Automatically finds the python packages in this repo for packaging.
    packages=find_packages(),

    # Signifies that this version works with python version 3.6 or higher.
    python_requires='>=3.6',

    # List of dependencies needed to run this project.
    # It's good practice to define a range of versions so that any minor
    # patch changes with bug fixes are automatically updated.
    # A complete list of range specifiers can be seen here:
    # https://pip.readthedocs.io/en/stable/reference/pip_install/#requirements-file-format
    install_requires=[
        # Example: 'flask>=1.1.1,<2'
        # This will install any flask version greater than 1.1.1 but less
        # than the major version 2.
        'Django~=2.2.5',
        'Click~=7.0.0',
        'djangorestframework~=3.10.2',
        'waitress~=1.3.0',
    ],

    entry_points={
        'console_scripts': [
            'app = server.core.command:main',
        ],
    },
)
