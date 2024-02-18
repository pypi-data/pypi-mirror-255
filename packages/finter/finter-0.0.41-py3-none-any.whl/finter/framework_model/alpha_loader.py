from __future__ import print_function

import finter
from finter.settings import api_client, logger
from finter.rest import ApiException

api_instance = finter.PortfolioApi(api_client)


class AlphaPositionLoader:
    def __init__(self, start, end, exchange, universe, instrument_type, freq, position_type, alpha_set):
        self.start = str(start)
        self.end = end
        self.exchange = exchange
        self.universe = universe
        self.instrument_type = instrument_type
        self.freq = freq
        self.position_type = position_type
        self.alpha_set = list(alpha_set) if isinstance(alpha_set, set) else alpha_set

    def to_dict(self):
        return {
            'start': self.start,
            'end': self.end,
            'exchange': self.exchange,
            'universe': self.universe,
            'instrument_type': self.instrument_type,
            'freq': self.freq,
            'position_type': self.position_type,
            'alpha_set': self.alpha_set
        }

    def get_alpha(self, identity_name):
        params = {**self.to_dict(), 'identity_name': identity_name}
        body = finter.BasePortfolioGetAlpha(**params)
        try:
            api_response = api_instance.portfolio_base_portfolio_get_alpha_create(body)
            return finter.to_dataframe(api_response.am, api_response.column_types)
        except ApiException as e:
            logger.error("Exception when calling AlphaPositionLoader->get_df: %s\n" % e)
        return
