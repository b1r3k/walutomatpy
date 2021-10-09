from enum import Enum, auto


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


class OrderCurrencyPair(AutoName):
    EURGBP = auto
    EURUSD = auto()
    EURCHF = auto()
    EURPLN = auto()
    GBPUSD = auto()
    GBPCHF = auto()
    GBPPLN = auto()
    USDCHF = auto()
    USDPLN = auto()
    CHFPLN = auto()
