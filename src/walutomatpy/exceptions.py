class WalutomatException(Exception):
    pass


class RetryError(WalutomatException):
    pass


class MissingVolume(WalutomatException):
    def __init__(self, missing_volume):
        self.missing = missing_volume

    def __str__(self):
        return f'Missing {self.missing} volume'

    def __float__(self):
        return float(self.missing)
