# walutomatpy

Python wrapper around [Walutomat API](https://api.walutomat.pl/v2.0.0/#section/Overview) version 2.0

## Installation

        $ pip install walutomatpy

## Usage

```python
from walutomatpy import WalutomatClient
from walutomatpy import AccountBalances


def get_client(api_key, path_to_private_key):
    with open(path_to_private_key, 'r') as fd:
        private_key = fd.read()
    client = WalutomatClient(api_key, private_key, 'api.walutomat.pl')
    return client


def example(api_client):
    balances_raw = api_client.get_account_balances()
    balances = AccountBalances(balances_raw)
    logger.info('Account balances: %s', balances)
    orders = api_client.get_p2p_active_orders()
    if orders:
        logger.info('Active orders:')
        for order in orders:
            logger.info(order)
    else:
        logger.info('No active orders!')

client = get_client(api_key, private_key_path)
example(client)
```
