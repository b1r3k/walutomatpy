class WalutomatException(Exception):
    pass


class RetryError(WalutomatException):
    pass


class InsufficientMarketDepth(RetryError):
    def __init__(self, pair, requested_volume, side, missing_volume, last_item_limit, attempts):
        self.pair = pair
        self.requested_volume = requested_volume
        self.side = side
        self.missing_volume = missing_volume
        self.last_item_limit = last_item_limit
        self.attempts = attempts
        super().__init__(
            f'Could not calculate {side} price for {pair} volume={requested_volume}; '
            f'missing_volume={missing_volume}; final_item_limit={last_item_limit}; attempts={attempts}'
        )


class MissingVolume(WalutomatException):
    def __init__(self, missing_volume):
        self.missing = missing_volume

    def __str__(self):
        return f'Missing {self.missing} volume'

    def __float__(self):
        return float(self.missing)
