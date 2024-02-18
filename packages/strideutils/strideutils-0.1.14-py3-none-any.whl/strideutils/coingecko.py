"""
Exposes an easy API to get prices from coingecko
"""

from typing import Dict

from strideutils import stride_requests
from strideutils.stride_config import config

COINGECKO_ENDPOINT = "https://pro-api.coingecko.com/"
COINGECKO_PRICE_QUERY = "api/v3/simple/price?ids={ticker}&vs_currencies=usd"


def get_token_price(
    ticker: str,
    api_token: str = config.COINGECKO_API_TOKEN,
    _cache: Dict[str, float] = {},
):
    '''
    Reads token price from coingecko
    If a redis_client is provided, then store the value.
    '''
    orig_ticker = ticker
    if ticker not in _cache:
        redemption_rate = float(1)
        coingecko_name = None
        # Get redemption rate for calculating st token prices
        if ticker.startswith('st') and ticker[3].isupper():
            redemption_rate = stride_requests.get_redemption_rate(ticker[2:])
            ticker = ticker[2:]

        # Fetch coingecko name if set, otherwise use name
        try:
            coingecko_name = config.get_chain(ticker=ticker).coingecko_name
        except AttributeError:
            coingecko_name = config.get_chain(ticker=ticker).name

        endpoint = COINGECKO_ENDPOINT + COINGECKO_PRICE_QUERY.format(ticker=coingecko_name)
        resp = stride_requests.request(
            endpoint,
            headers={'x-cg-pro-api-key': api_token},
        )
        _cache[orig_ticker] = resp[coingecko_name]['usd'] * redemption_rate
    return _cache[orig_ticker]
