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

    def test_order_currency_enum_supports_requested_pairs(self):
        pairs = [
            'EURGBP', 'EURUSD', 'EURCHF', 'EURPLN', 'GBPUSD', 'GBPCHF', 'GBPPLN',
            'USDCHF', 'USDPLN', 'CHFPLN', 'EURSEK', 'EURNOK', 'EURDKK', 'EURCZK',
            'CZKPLN', 'DKKPLN', 'NOKPLN', 'SEKPLN', 'AUDPLN', 'CADPLN', 'CNYPLN',
            'HKDPLN', 'HUFPLN', 'ILSPLN', 'JPYPLN', 'MXNPLN', 'NZDPLN', 'RONPLN',
            'SGDPLN', 'TRYPLN', 'ZARPLN', 'EURAUD', 'EURCAD', 'EURCNY', 'EURHKD',
            'EURHUF', 'EURILS', 'EURJPY', 'EURMXN', 'EURNZD', 'EURRON', 'EURSGD',
            'EURTRY', 'EURZAR',
        ]

        for pair in pairs:
            with self.subTest(pair=pair):
                self.assertEqual(str(OrderCurrencyEnum(pair)), pair)

    def test_parsing_nanoseconds(self):
        datetime_str = '2022-08-03T09:50:16.692380437Z'
        raw_order = read_fixture('order_result.json')
        raw_order['updateTs'] = datetime_str
        WalutomatOrder(**raw_order)


class TestAccountBalances(unittest.TestCase):
    def test_account_balances_testing(self):
        raw_balance = read_fixture('account_balances.json')
        balances = AccountBalances(raw_balance)
        self.assertEqual(balances[OrderCurrencyEnum.EUR].total, Decimal('300.33'))
