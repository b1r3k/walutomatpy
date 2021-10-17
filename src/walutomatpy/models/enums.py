from enum import Enum, auto
from dataclasses import dataclass


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __str__(self):
        return self.value


class OrderStatusEnum(AutoName):
    ACTIVE = auto()
    CLOSED = auto()


class OrderTypeEnum(AutoName):
    BUY = auto()
    SELL = auto()


class OrderCurrencyEnum(AutoName):
    EUR = auto()
    GBP = auto()
    USD = auto()
    CHF = auto()
    PLN = auto()


@dataclass
class OrderCurrencyPair:
    base: OrderCurrencyEnum
    counter: OrderCurrencyEnum

    def __init__(self, pair: str = None, **kwargs):
        if pair is None:
            self.base = kwargs['base']
            self.counter = kwargs['counter']
        else:
            base = pair[0:3]
            counter = pair[3:6]
            self.base = OrderCurrencyEnum(base)
            self.counter = OrderCurrencyEnum(counter)

    def __str__(self):
        return f'{str(self.base)}{str(self.counter)}'
