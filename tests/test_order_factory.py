from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from decimal import Decimal

from walutomatpy import WalutomatClient
from walutomatpy import WalutomatOrder
from walutomatpy import AccountBalances
from walutomatpy.models.order_factory import WalutomatOrderFactory
from walutomatpy import OrderCurrencyPair, OrderCurrencyEnum, OrderTypeEnum

from . import read_fixture


class TestOrderFactory(TestCase):
    UUID4 = '3d4a2181-44c7-4b8a-a82d-f889dcba401f'

    def setUp(self) -> None:
        self.raw_order = read_fixture('order_result.json')
        self.raw_balances = read_fixture('account_balances.json')
        self.order = WalutomatOrder(**self.raw_order)
        self.client_mock = MagicMock(spec=WalutomatClient)
        self.client_mock.submit_p2p_order.return_value = dict(orderId="2035e361-e672-457a-9c3c-0e86e5ff54d6")
        self.client_mock.get_p2p_order_by_id.return_value = [self.raw_order]
        self.client_mock.get_account_balances.return_value = self.raw_balances
        self.factory = WalutomatOrderFactory(self.client_mock)
        p = patch('walutomatpy.models.order_factory.uuid.uuid4')
        self.uuid_mock = p.start()
        self.uuid_mock.return_value = self.UUID4
        self.addCleanup(p.stop)

    def test_order_issuence(self):
        pair = OrderCurrencyPair(base=OrderCurrencyEnum.EUR, counter=OrderCurrencyEnum.PLN)
        result = self.factory.issue_order(OrderTypeEnum.SELL, pair, 1000, pair.base, 4.50)
        self.assertEqual(result[0], self.order)

    def test_order_canceling(self):
        self.factory.cancel(self.order.orderId)
        self.client_mock.cancel_p2p_order.assert_called_with(self.order.orderId)

    def test_order_execution_status(self):
        result = self.factory.is_executed(self.order.orderId)
        self.client_mock.get_p2p_order_by_id.assert_called_with(self.order.orderId)
        self.assertFalse(result)

    def test_sell_all_balance_base(self):
        base = OrderCurrencyEnum.EUR
        counter = OrderCurrencyEnum.PLN
        pair = OrderCurrencyPair(base=base, counter=counter)
        limit = 4.51
        self.factory.sell_all_balance(pair, base, limit)
        self.client_mock.submit_p2p_order.assert_called_with(self.UUID4, pair, OrderTypeEnum.SELL, 200, base, limit)

    def test_buy_all_balance_base(self):
        base = OrderCurrencyEnum.EUR
        counter = OrderCurrencyEnum.PLN
        pair = OrderCurrencyPair(base=base, counter=counter)
        limit = 4.51
        volume_to_buy = Decimal('33.25942350332594392232206868')
        self.factory.buy_all_balance(pair, base, limit)
        self.client_mock.submit_p2p_order.assert_called_with(self.UUID4, pair, OrderTypeEnum.BUY, volume_to_buy, base,
                                                             limit)
