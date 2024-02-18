"""
#
# Test base class
#
# Copyright(c) 2018, Carium, Inc. All rights reserved.
#
"""

import unittest

from cariutils.mock import MockManager


class TestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock = MockManager()

    def tearDown(self) -> None:
        self.mock.cleanup()
