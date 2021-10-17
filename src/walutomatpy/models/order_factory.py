import uuid
from decimal import Decimal

from .enums import OrderTypeEnum, OrderCurrencyPair, OrderCurrencyEnum
from .order import WalutomatOrder
from .account import AccountBalances


class WalutomatOrderFactory:
    def __init__(self, client):
        self._client = client

    def issue_order(self,
                    order_type: OrderTypeEnum,
                    currency_pair: OrderCurrencyPair,
                    volume,
                    volume_currency: OrderCurrencyEnum,
                    price_limit) -> WalutomatOrder:
        order_id = uuid.uuid4()
        resp = self._client.submit_p2p_order(str(order_id), currency_pair, order_type, volume, volume_currency,
                                             price_limit)
        raw_orders = self._client.get_p2p_order_by_id(resp['orderId'])
        return list(WalutomatOrder(**raw_order) for raw_order in raw_orders)

    def sell_all_balance(self, currency_pair: OrderCurrencyPair, currency: OrderCurrencyEnum, price_limit) -> \
            WalutomatOrder:
        """
        Hint: it's easier to issue sell of counter currency to buy base currency becasue we can use account balance
        instead of calculating how much should we buy at given price limit

        :param currency:
        :param price_limit: should be price as BASE_CURRENCY:COUNTER_CURRENCY e.g. EURPLN=4.5797 price
        :return:
        """
        balances_resp = self._client.get_account_balances()
        balances = AccountBalances(balances_resp)
        return self.issue_order(OrderTypeEnum.SELL, currency_pair, balances[currency].available, currency, price_limit)

    def buy_all_balance(self, currency_pair: OrderCurrencyPair, currency: OrderCurrencyEnum, price_limit) -> \
            WalutomatOrder:
        """
        :param currency:
        :param price_limit: should be price as BASE_CURRENCY:COUNTER_CURRENCY e.g. EURPLN=4.5797 price
                            same as when selling!
        :return:
        """
        balances_resp = self._client.get_account_balances()
        balances = AccountBalances(balances_resp)
        counter_currency = currency_pair.counter
        volume_to_buy = balances[counter_currency].available / Decimal(price_limit)
        return self.issue_order(OrderTypeEnum.BUY, currency_pair, volume_to_buy, currency, price_limit)

    def cancel(self, order_id):
        self._client.cancel_p2p_order(order_id)

    def is_executed(self, order_id):
        raw_orders = self._client.get_p2p_order_by_id(order_id)
        orders = list(WalutomatOrder(**raw_order) for raw_order in raw_orders)
        return all(order.is_executed() for order in orders)
