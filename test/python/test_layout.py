# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

import unittest

from qiskit.mapper import Layout
from .common import QiskitTestCase


class LayoutTest(QiskitTestCase):

    def test_layout_from_dict(self):
        layout = Layout({('qr', 0): 0,
                         ('qr', 1): 1,
                         ('qr', 2): 2})

        self.assertEqual(layout[('qr', 0)], 0)
        self.assertEqual(layout[('qr', 1)], 1)
        self.assertEqual(layout[('qr', 2)], 2)
        self.assertEqual(layout[0], ('qr', 0))
        self.assertEqual(layout[1], ('qr', 1))
        self.assertEqual(layout[2], ('qr', 2))

    def test_layout_set(self):
        layout = Layout()
        layout[('qr', 0)] = 0

        self.assertEqual(layout[('qr', 0)], 0)
        self.assertEqual(layout[0], ('qr', 0))

    def test_layout_get_logical(self):
        layout_dict = {('qr', 0): 0,
                       ('qr', 1): 1,
                       ('qr', 2): 2}
        layout = Layout(layout_dict)
        self.assertDictEqual(layout_dict, layout.get_logical())

    def test_layout_add_logical(self):
        layout = Layout()
        layout[('qr,0')] = 0
        layout.add_logical(('qr', 1))

        self.assertEqual(layout[('qr', 1)], 1)
        self.assertEqual(layout[1], ('qr', 1))


if __name__ == '__main__':
    unittest.main()
