import uuid

from .enums import OrderTypeEnum, OrderCurrencyPair, OrderCurrencyEnum
from .order import WalutomatOrder
from .account import AccountBalances


class WalutomatOrderFactory:
    def __init__(self, client, base_currency: OrderCurrencyEnum, counter_currency: OrderCurrencyEnum):
        self._client = client
        self._base_currency = base_currency
        self._counter_currency = counter_currency
        self._currency_pair = OrderCurrencyPair(base_currency.value + counter_currency.value)

    @property
    def currency_pair(self):
        return self._currency_pair

    def issue_order(self,
                    order_type: OrderTypeEnum,
                    volume,
                    volume_currency: OrderCurrencyEnum,
                    price_limit) -> WalutomatOrder:
        order_id = uuid.uuid4()
        resp = self._client.submit_p2p_order(str(order_id), self._currency_pair, order_type, volume, volume_currency,
                                             price_limit)
        raw_orders = self._client.get_p2p_order_by_id(resp['orderId'])
        return list(WalutomatOrder(**raw_order) for raw_order in raw_orders)

    def sell_all_balance(self, currency: OrderCurrencyEnum, price_limit) -> WalutomatOrder:
        balances_resp = self._client.get_account_balances()
        balances = AccountBalances(balances_resp)
        return self.issue_order(OrderTypeEnum.SELL, balances[currency].available, currency, price_limit)

    def buy_all_balance(self, currency: OrderCurrencyEnum, price_limit) -> WalutomatOrder:
        balances_resp = self._client.get_account_balances()
        balances = AccountBalances(balances_resp)
        return self.issue_order(OrderTypeEnum.BUY, balances[currency].available, currency, price_limit)

    def sell_all_base_currency(self, price_limit) -> WalutomatOrder:
        """
        :param price_limit: should be price as BASE_CURRENCY:COUNTER_CURRENCY e.g. EURPLN=4.5797 price
        """
        balances_resp = self._client.get_account_balances()
        balances = AccountBalances(balances_resp)
        currency = self._base_currency
        return self.issue_order(OrderTypeEnum.SELL, balances[currency].available, currency, price_limit)[0]

    def sell_all_counter_currency(self, price_limit) -> WalutomatOrder:
        """
        it sells counter currency for base currency or in other words it buys base currency for counter currency

        :param price_limit: should be price as BASE_CURRENCY:COUNTER_CURRENCY e.g. EURPLN=4.5797 price
        """
        balances_resp = self._client.get_account_balances()
        balances = AccountBalances(balances_resp)
        currency = self._counter_currency
        # it's easier to issue sell of counter currency to buy base currency becasue we can use account balance
        # instead of calculating how much should we buy at given price limit
        return self.issue_order(OrderTypeEnum.SELL, balances[currency].available, currency, price_limit)[0]

    def cancel(self, order_id):
        self._client.cancel_p2p_order(order_id)

    def is_executed(self, order_id):
        resp = self._client.get_p2p_order_by_id(order_id)
        order = WalutomatOrder(**resp)
        return order.is_executed()
