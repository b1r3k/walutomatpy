from dataclasses import dataclass, fields, asdict
from decimal import Decimal
from datetime import datetime

from .enums import OrderTypeEnum, OrderCurrencyPair, OrderCurrencyEnum, OrderStatusEnum


# '2018-02-02T10:06:01.111Z'
DATE_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'


@dataclass(repr=True)
class WalutomatOrder:
    # required
    orderId: str
    submitId: str
    submitTs: datetime
    updateTs: datetime
    status: OrderStatusEnum
    completion: Decimal
    currencyPair: OrderCurrencyPair
    buySell: OrderTypeEnum
    volume: Decimal
    volumeCurrency: OrderCurrencyEnum
    # additional
    limitPrice: Decimal
    soldAmount: Decimal
    soldCurrency: OrderCurrencyEnum
    boughtAmount: Decimal
    boughtCurrency: OrderCurrencyEnum
    commissionAmount: Decimal
    commissionCurrency: OrderCurrencyEnum
    commissionRate: Decimal

    def __init__(self, **kwargs):
        submit_ts = kwargs.get('submitTs')
        if submit_ts:
            self.submitTs = datetime.strptime(submit_ts, DATE_FMT)
        update_ts = kwargs.get('updateTs')
        if update_ts:
            self.updateTs = datetime.strptime(update_ts, DATE_FMT)
        obj_field_types = {field.name: field.type for field in fields(self)}
        for arg_name, arg_value in kwargs.items():
            field_type = obj_field_types.get(arg_name)
            field_value = getattr(self, arg_name, None)
            if field_value is None and field_type:
                setattr(self, arg_name, field_type(arg_value))

    def is_executed(self):
        return self.completion == 100

    def is_sell(self):
        return self.buySell == OrderTypeEnum.BUY

    def __str__(self):
        obj_field_types = {field.name: field.type for field in fields(self)}
        _asdict = {}
        for field_name in obj_field_types.keys():
            value = getattr(self, field_name, None)
            if value:
                _asdict[field_name] = value
        return str(_asdict)

    def __repr__(self):
        return self.__str__()
