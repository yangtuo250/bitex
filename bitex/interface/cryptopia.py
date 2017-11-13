# Import Built-Ins
import logging

# Import Homebrew
from bitex.api.REST.cryptopia import CryptopiaREST
from bitex.interface.rest import RESTInterface
from bitex.utils import check_and_format_pair

# Init Logging Facilities
log = logging.getLogger(__name__)


class Cryptopia(RESTInterface):
    def __init__(self, **APIKwargs):
        super(Cryptopia, self).__init__('Cryptopia', CryptopiaREST(**APIKwargs))

    def _get_supported_pairs(self):
        r = self.request('GET', 'GetTradePairs').json()
        pairs = [entry['Label'].replace('/', '_') for entry in r['Data']]
        return pairs

    # Public Endpoints
    @check_and_format_pair
    def ticker(self, pair, *args, **kwargs):
        return self.request('GET', 'GetMarket/' + pair, params=kwargs)

    @check_and_format_pair
    def order_book(self, pair, *args, **kwargs):
        return self.request('GET', 'GetMarketOrders/' + pair, params=kwargs)

    @check_and_format_pair
    def trades(self, pair, *args, **kwargs):
        return self.request('GET', 'GetMarketHistory/' + pair, params=kwargs)

    # Private Endpoints
    def _place_order(self, pair, price, size, side, *args, **kwargs):
        payload = {'Market': pair, 'Type': side, 'Rate': price, 'Amount': size}
        payload.update(kwargs)
        return self.request('POST', 'SubmitTrade', params=payload,
                            authenticate=True)

    @check_and_format_pair
    def ask(self, pair, price, size, *args, **kwargs):
        return self._place_order(pair, price, size, 'Sell', *args, **kwargs)

    @check_and_format_pair
    def bid(self, pair, price, size, *args, **kwargs):
        return self._place_order(pair, price, size, 'Buy', *args, **kwargs)

    def order_status(self, order_id, *args, **kwargs):
        raise NotImplementedError

    def open_orders(self, *args, **kwargs):
        return self.request('POST', 'GetOpenOrders', params=kwargs,
                            authenticate=True)

    def cancel_order(self, *order_ids, **kwargs):
        results = []
        payload = {'Type': 'Trade'}
        for oid in order_ids:
            payload.update({'OrderId': oid})
            r = self.request('POST', 'CancelTrade', params=payload,
                             authenticate=True)
            results.append(r)
        return results if len(results) > 1 else results[0]

    def wallet(self, *args, **kwargs):
        return self.request('POST', 'GetBalance', params=kwargs,
                            authenticate=True)
