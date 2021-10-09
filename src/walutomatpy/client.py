from datetime import datetime
import base64
import urllib.parse
from urllib.parse import urljoin, urlsplit
from pprint import pformat

import requests
from OpenSSL import crypto


class WalutomatApiException(Exception):
    def __init__(self, request, error_response):
        self._request = request
        self._errors = error_response.get('errors')

    def _parse_errors(self, error):
        key, desc, data = error.get('key'), error.get('description'), error.get('errorData')
        return key, desc, data

    @property
    def short_str(self):
        s = ''
        for error in self._errors:
            key, desc, data = self._parse_errors(error)
            s = f'{key}: {desc}'
        return s

    def __str__(self):
        s = f'{self._request.method} {self._request.url}\n{self._request.body}'
        s += '--- HEADERS ---'
        for header, value in self._request.headers.items():
            s += f'{header}: {value}\n'
        s += '--- ERRORS ---'
        for error in self._errors:
            key, desc, data = self._parse_errors(error)
            s += f'{key}: {desc}'
            if data:
                s += f'\n{data}'
        return s

    def __repr__(self):
        return f'<WalutomatApiException: {self.short_str} @ {self._request.url}>\n\nRequest: {self._request}'


class WalutomatClient:

    def __init__(self, api_key, private_key, base_url='api.walutomat.pl', dryRun=False):
        self._api_key = api_key
        self._raw_private_key = private_key
        self._base_url = base_url
        self._private_key = None
        self._session = None
        self._dryRun = dryRun

    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                'X-API-Key': self._api_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            })
        return self._session

    @property
    def private_key(self):
        if self._private_key is None:
            self._private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, self._raw_private_key)
        return self._private_key

    def get_signature(self, uri, timestamp, body=None):
        parsed_url = urlsplit(uri)
        if body is not None:
            data_to_sign = f'{timestamp}{parsed_url.path}{body}'
        else:
            data_to_sign = f'{timestamp}{parsed_url.path}'
            if parsed_url.query:
                data_to_sign += f'?{parsed_url.query}'
        signature = crypto.sign(self.private_key, data_to_sign, 'sha256')
        signature_base64 = base64.b64encode(signature)
        return signature_base64

    def request(self, method, endpoint_uri, headers=None, files=None, data=None,
                params=None, auth=None, cookies=None, hooks=None, json=None, **kwargs):
        kwargs.setdefault('timeout', (3.05, 10))
        url = urljoin(f'https://{self._base_url}', endpoint_uri)
        req = requests.Request(method, url, headers, files, data, params, auth, cookies, hooks, json)
        prepped = self.session.prepare_request(req)
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        signature_base64 = self.get_signature(prepped.url, timestamp, prepped.body)
        _headers = {
            'X-API-Signature': signature_base64,
            'X-API-Timestamp': timestamp,
        }
        headers = headers or {}
        headers.update(_headers)
        prepped.headers.update(headers)
        resp = self.session.send(prepped, **kwargs)
        json = resp.json()
        if json['success']:
            return json
        if json.get('errors'):
            raise WalutomatApiException(resp.request, json)

    def get_account_balances(self):
        data = self.request('GET', '/api/v2.0.0/account/balances')
        return data.get('result')

    def get_account_history(self, date_from=None, date_to=None, currencies=None, operation_type=None, item_limit=200,
                            continue_from=None, sort_order='DESC'):
        params = dict(
            dateFrom=date_from,
            dateTo=date_to,
            currencies=currencies,
            operationType=operation_type,
            itemLimit=item_limit,
            continueFrom=continue_from,
            sort_order=sort_order
        )
        while True:
            resp = self.request('GET', '/api/v2.0.0/account/history', params=params)
            json = resp.json()
            items = json.get('result', [])
            for item in items:
                yield item
            if len(items) != item_limit:
                break
            last_history_item_id = items[-1].get('historyItemId')
            params.update(dict(continueFrom=last_history_item_id))

    def get_p2p_best_offers(self, currency_pair):
        params = dict(
            currencyPair=currency_pair
        )
        data = self.request('GET', '/api/v2.0.0/market_fx/best_offers', params=params)
        result = data.get('result')
        return result

    def get_p2p_best_offers_detailed(self, currency_pair, item_limit=10):
        params = dict(
            currencyPair=currency_pair,
            itemLimit=item_limit
        )
        data = self.request('GET', '/api/v2.0.0/market_fx/best_offers/detailed', params=params)
        return data.get('result')

    def get_p2p_active_orders(self, item_limit=10):
        params = dict(
            itemLimit=item_limit
        )
        while True:
            data = self.request('GET', '/api/v2.0.0/market_fx/orders/active', params=params)
            items = data.get('result', [])
            for item in items:
                yield item
            if len(items) != item_limit:
                break
            last_item_pos = items[-1].get('submitTs')
            params.update(dict(olderThan=last_item_pos))

    def get_p2p_order_by_id(self, order_id):
        params = dict(
            orderId=order_id,
        )
        data = self.request('GET', '/api/v2.0.0/market_fx/orders', params=params)
        return data.get('result')

    def submit_p2p_order(self, order_id, currency_pair, buy_sell, volume, volume_currency, limit_price, dry=False):
        """
        :param order_id: Unique exchange identifier assigned by sender (GUID or UUID), required when not dry run mode,
                        must not be used when dryRun=true
        """
        is_dry_run = self._dryRun or dry
        params = dict(
            currencyPair=currency_pair,
            buySell=str(buy_sell),
            volume=volume,
            volumeCurrency=volume_currency,
            limitPrice=limit_price,
            dryRun=is_dry_run
        )
        if not is_dry_run:
            params.update(dict(submitId=order_id))

        data = self.request('POST', '/api/v2.0.0/market_fx/orders', data=params)
        return data.get('result')

    def cancel_p2p_order(self, order_id):
        params = dict(
            order_id=order_id
        )
        data = self.request('POST', '/api/v2.0.0/market_fx/orders/close', data=params)
        return data.get('result')
