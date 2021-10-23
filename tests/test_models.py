import unittest
from decimal import Decimal

from . import read_fixture

from walutomatpy import WalutomatOrder
from walutomatpy import OrderCurrencyPair, OrderCurrencyEnum
from walutomatpy import AccountBalances


class TestWalutomatOrder(unittest.TestCase):
    def test_order_parsing(self):
        raw_order = read_fixture('order_result.json')
        order = WalutomatOrder(**raw_order)
        self.assertTrue(order.orderId)

    def test_order_currency_pair_serialization(self):
        pair = OrderCurrencyPair(base=OrderCurrencyEnum.EUR, counter=OrderCurrencyEnum.PLN)
        self.assertEqual(str(pair), 'EURPLN')


class TestAccountBalances(unittest.TestCase):
    def test_account_balances_testing(self):
        raw_balance = read_fixture('account_balances.json')
        balances = AccountBalances(raw_balance)
        self.assertEqual(balances[OrderCurrencyEnum.EUR].total, Decimal('300.33'))
