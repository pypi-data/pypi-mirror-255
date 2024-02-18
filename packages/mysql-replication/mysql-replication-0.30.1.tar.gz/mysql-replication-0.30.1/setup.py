#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command

from pathlib import Path
import sys

tests_require = []

# add unittest2 to tests_require for python < 2.7
if sys.version_info < (2, 7):
    tests_require.append("unittest2")


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """
        Finds all the tests modules in tests/, and runs them.
        """
        from pymysqlreplication import tests
        import unittest

        unittest.main(tests, argv=sys.argv[:1])


version = "0.30.1"
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="mysql-replication",
    version=version,
    url="https://github.com/julien-duponchelle/python-mysql-replication",
    author="Julien Duponchelle",
    author_email="julien@duponchelle.info",
    description=("Pure Python Implementation of MySQL replication protocol "
                 "build on top of PyMYSQL."),
    license="Apache 2",
    packages=["pymysqlreplication",
              "pymysqlreplication.constants",
              "pymysqlreplication.tests"],
    cmdclass={"test": TestCommand},
    extras_require={'test': tests_require},
    install_requires=["packaging",'pymysql>=0.10'],
)
