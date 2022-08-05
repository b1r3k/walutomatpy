from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal

import requests

from walutomatpy import WrappedWalutomatClient
from walutomatpy import WalutomatOrder
from walutomatpy import AccountBalances
from walutomatpy import WalutomatTrader
from walutomatpy import OrderCurrencyPair, OrderCurrencyEnum, OrderTypeEnum
from walutomatpy import Offer
from walutomatpy.trader import get_price_by_volume, MissingVolume

from . import read_fixture


class TestCaseHTTPMocks(TestCase):
    def setUp(self) -> None:
        super().setUp()
        p = patch('walutomatpy.client.requests')
        self.requests_mock = p.start()
        self.requests_mock.return_value = requests.Request
        self.session_mock = MagicMock(spec=requests.Session())
        self.prepared_request = MagicMock(spec=requests.PreparedRequest())
        self.session_mock.prepare_request.return_value = self.prepared_request
        self.prepared_request.url = 'URL'
        self.requests_mock.Session.return_value = self.session_mock
        self.addCleanup(p.stop)


class TestCaseBase(TestCaseHTTPMocks):
    private_key = 'LOADED_PRIVATE_KEY'
    signature = b'SIG'

    def setUp(self) -> None:
        super().setUp()
        p = patch('walutomatpy.client.crypto.load_privatekey')
        self.load_privatekey_mock = p.start()
        self.load_privatekey_mock.return_value = self.private_key
        self.addCleanup(p.stop)
        p = patch('walutomatpy.client.crypto.sign')
        self.sign_mock = p.start()
        self.sign_mock.return_value = self.signature
        self.addCleanup(p.stop)


class TestWalutomatTrader(TestCaseBase):
    UUID4 = '3d4a2181-44c7-4b8a-a82d-f889dcba401f'

    def setUp(self) -> None:
        super().setUp()
        self.raw_order = read_fixture('order_result.json')
        self.raw_balances = read_fixture('account_balances.json')
        self.balances = AccountBalances(self.raw_balances)
        self.order = WalutomatOrder(**self.raw_order)
        self.client_mock = MagicMock(spec=WrappedWalutomatClient)
        self.client_mock.submit_p2p_order.return_value = "2035e361-e672-457a-9c3c-0e86e5ff54d6"
        self.client_mock.get_p2p_order_by_id.return_value = [self.order]
        self.client_mock.get_account_balances.return_value = self.balances
        self.trader = WalutomatTrader(self.client_mock)
        p = patch('walutomatpy.trader.uuid.uuid4')
        self.uuid_mock = p.start()
        self.uuid_mock.return_value = self.UUID4
        self.addCleanup(p.stop)

    def test_order_issuence(self):
        pair = OrderCurrencyPair(base=OrderCurrencyEnum.EUR, counter=OrderCurrencyEnum.PLN)
        result = self.trader.issue_order(OrderTypeEnum.SELL, pair, 1000, pair.base, 4.50)
        self.assertEqual(result, self.order)

    def test_order_canceling(self):
        self.trader.cancel(self.order.orderId)
        self.client_mock.cancel_p2p_order.assert_called_with(self.order.orderId)

    def test_sell_all_balance_base(self):
        base = OrderCurrencyEnum.EUR
        counter = OrderCurrencyEnum.PLN
        pair = OrderCurrencyPair(base=base, counter=counter)
        limit = 4.51
        self.trader.sell_all_balance(pair, base, limit)
        self.client_mock.submit_p2p_order.assert_called_with(self.UUID4, pair, OrderTypeEnum.SELL, 200, base, limit)

    def test_buy_all_balance_base(self):
        base = OrderCurrencyEnum.EUR
        counter = OrderCurrencyEnum.PLN
        pair = OrderCurrencyPair(base=base, counter=counter)
        limit = 4.51
        volume_to_buy = Decimal('33.25942350332594392232206868')
        self.trader.buy_all_balance(pair, base, limit)
        self.client_mock.submit_p2p_order.assert_called_with(self.UUID4, pair, OrderTypeEnum.BUY, volume_to_buy, base,
                                                             limit)


class TestPricePerVolume(TestCase):
    def test_happy_path(self):
        offers = [Offer(10, 100), Offer(20, 150), Offer(10, 200)]
        result = get_price_by_volume(offers, 200)
        expected = (100 * 10 + 100 * 20) / 200
        self.assertEqual(result, expected)

    def test_not_enough_volume(self):
        offers = [Offer(10, 100), Offer(20, 150), Offer(10, 200)]
        with self.assertRaises(MissingVolume) as ex:
            get_price_by_volume(offers, 500)
            self.assertEqual(float(ex), 50.0)
