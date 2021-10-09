from dataclasses import dataclass
from decimal import Decimal

from .enums import OrderTypeEnum, OrderCurrencyPair, OrderCurrencyEnum


@dataclass
class AccountCurrencyBalance:
    currency: OrderCurrencyEnum
    total: Decimal
    available: Decimal
    reserved: Decimal

    def __init__(self, currency, total, available, reserved):
        self.currency = OrderCurrencyEnum(currency)
        self.total = Decimal(total)
        self.available = Decimal(available)
        self.reserved = Decimal(reserved)

    def __str__(self):
        return f'{self.total:10.6} {self.currency} = {self.available:10.6} + {self.reserved:10.6}'


class AccountBalances:
    def __init__(self, api_response: dict):
        self._balances = {}
        for balance in api_response:
            bal_currency = OrderCurrencyEnum(balance['currency'])
            self._balances[bal_currency] = AccountCurrencyBalance(balance['currency'], balance['balanceTotal'],
                                                                  balance['balanceAvailable'],
                                                                  balance['balanceReserved'])

    def __str__(self):
        s = ''
        for currency, balance in self._balances.items():
            s += f'{balance}\n'
        return s

    def __getitem__(self, item):
        return self._balances[item]
