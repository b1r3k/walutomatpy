import time
import uuid
from decimal import Decimal
from typing import List
import math

from .models.enums import OrderTypeEnum, OrderCurrencyPair, OrderCurrencyEnum
from .models.enums import Offer
from .models.order import WalutomatOrder
from .models.account import AccountBalances
from . import WrappedWalutomatClient
from .exceptions import RetryError, MissingVolume


def get_price_by_volume(offers: List[Offer], volume) -> float:
    """
    gets average price from list of offers
    :param offers: sorted list of offers
    :param volume:
    :return:
    """
    cum_volume = 0
    cum_offers = []
    for offer in offers:
        missing_volume = volume - cum_volume
        if offer.volume <= missing_volume:
            cum_offers.append((offer.volume, offer.price))
            cum_volume += offer.volume
        else:
            cum_offers.append((missing_volume, offer.price))
            cum_volume += missing_volume
            break
    missing_volume = volume - cum_volume
    if missing_volume > 0:
        raise MissingVolume(missing_volume)
    avg_price = sum(map(lambda o: o[0] * o[1], cum_offers)) / cum_volume
    return avg_price


class WalutomatTrader:
    def __init__(self, client: WrappedWalutomatClient):
        self._client = client

    def get_order_by_id(self, order_id):
        orders = self._client.get_p2p_order_by_id(order_id)
        return orders[0]

    def issue_order(self,
                    order_type: OrderTypeEnum,
                    currency_pair: OrderCurrencyPair,
                    volume,
                    volume_currency: OrderCurrencyEnum,
                    price_limit) -> WalutomatOrder:
        order_id = uuid.uuid4()
        walutomat_order_id = self._client.submit_p2p_order(str(order_id), currency_pair, order_type, volume,
                                                           volume_currency,
                                                           price_limit)
        orders = self.get_order_by_id(walutomat_order_id)
        return orders

    def get_account_balances(self):
        return self._client.get_account_balances()

    def sell_all_balance(self, currency_pair: OrderCurrencyPair, currency: OrderCurrencyEnum, price_limit) -> \
            WalutomatOrder:
        """
        Hint: it's easier to issue sell of counter currency to buy base currency becasue we can use account balance
        instead of calculating how much should we buy at given price limit

        :param currency:
        :param price_limit: should be price as BASE_CURRENCY:COUNTER_CURRENCY e.g. EURPLN=4.5797 price
        :return:
        """
        balances = self._client.get_account_balances()
        return self.issue_order(OrderTypeEnum.SELL, currency_pair, balances[currency].available, currency, price_limit)

    def buy_all_balance(self, currency_pair: OrderCurrencyPair, currency: OrderCurrencyEnum, price_limit) -> \
            WalutomatOrder:
        """
        :param currency:
        :param price_limit: should be price as BASE_CURRENCY:COUNTER_CURRENCY e.g. EURPLN=4.5797 price
                            same as when selling!
        :return:
        """
        balances = self._client.get_account_balances()
        counter_currency = currency_pair.counter
        volume_to_buy = balances[counter_currency].available / Decimal(price_limit)
        return self.issue_order(OrderTypeEnum.BUY, currency_pair, volume_to_buy, currency, price_limit)

    def cancel(self, order_id):
        self._client.cancel_p2p_order(order_id)

    def wait_to_fill_order(self, order_id, update_delay=10):
        while True:
            order = self.get_order_by_id(order_id)
            if order.is_executed():
                return True
            time.sleep(update_delay)

    def get_best_price_per_volume(self, pair: OrderCurrencyPair, volume: int, *, item_limit=10):
        retry = 3
        while retry:
            bids, asks = self._client.get_p2p_best_offers_detailed(pair, item_limit)
            try:
                best_bid = get_price_by_volume(bids, volume)
                best_ask = get_price_by_volume(asks, volume)
                return best_bid, best_ask
            except MissingVolume:
                # fetch 20% more orders to get enough volume
                item_limit = math.ceil(1.2 * item_limit)
                retry -= 1
                continue
        raise RetryError()
