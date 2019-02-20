# -*- coding: utf-8 -*-

# Copyright 2019, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""Qiskit property based tests."""

import os


def load_tests(loader, standard_tests, pattern):
    """
    test suite for unittest discovery
    """
    this_dir = os.path.dirname(__file__)
    if pattern in ['test*.py', '*_test.py']:
        package_tests = loader.discover(start_dir=this_dir, pattern=pattern)
        standard_tests.addTests(package_tests)
    return standard_tests
