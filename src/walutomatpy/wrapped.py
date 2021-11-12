import uuid
from decimal import Decimal
from typing import List, Tuple

from .models.enums import Offer
from .models.order import WalutomatOrder
from .models.account import AccountBalances
from . import WalutomatClient


class WrappedWalutomatClient(WalutomatClient):
    def get_account_balances(self) -> AccountBalances:
        result = super().get_account_balances()
        return AccountBalances(result)

    def get_p2p_best_offers_detailed(self, currency_pair, item_limit=10) -> Tuple[List, List]:
        result = super().get_p2p_best_offers_detailed(currency_pair, item_limit)
        bids = (Offer(offer['price'], offer['volume']) for offer in result.get('bids', []))
        sorted_bids = sorted(bids, key=lambda o: o.price, reverse=True)
        asks = (Offer(offer['price'], offer['volume']) for offer in result.get('asks', []))
        sorted_asks = sorted(asks, key=lambda o: o.price)
        return sorted_bids, sorted_asks

    def get_p2p_active_orders(self, item_limit=10):
        for result in super().get_p2p_active_orders(item_limit):
            yield WalutomatOrder(**result)

    def get_p2p_order_by_id(self, order_id) -> List[WalutomatOrder]:
        result = super().get_p2p_order_by_id(order_id)
        return list(WalutomatOrder(**raw_order) for raw_order in result)

    def submit_p2p_order(self, order_id, currency_pair, buy_sell, volume, volume_currency, limit_price, dry=False):
        result = super().submit_p2p_order(order_id, currency_pair, buy_sell, volume, volume_currency, limit_price, dry)
        return result['orderId']
