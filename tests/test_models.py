import unittest

from . import read_fixture

from walutomatpy import WalutomatOrder


class TestWalutomatOrder(unittest.TestCase):
    def test_order_parsing(self):
        raw_order = read_fixture('order_result.json')
        order = WalutomatOrder(**raw_order)
        self.assertTrue(order.orderId)
