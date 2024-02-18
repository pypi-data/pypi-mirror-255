from __future__ import print_function

from finter.rest import ApiException

import finter
from finter.settings import api_client, logger

api_instance = finter.AlphaApi(api_client)


class ContentModelLoader(object):
    @classmethod
    def load(cls, key):
        return GetCMGetDf(identity_name=key)


class GetCMGetDf(object):
    def __init__(self, identity_name):
        self.identity_name = identity_name

    def get_df(self, start, end, code_format='fnguide_to_quantit', **kwargs):
        # if start or end is str, convert it to str
        param = {
            "identity_name": self.identity_name,
            "start": str(start),
            "end": str(end)
        }
        if ('fnguide' in self.identity_name) and (code_format=='fnguide_to_quantit'):
            param['code_format'] = 'fnguide_to_quantit'
        try:
            api_response = api_instance.alpha_base_alpha_cm_retrieve(**param, **kwargs)
            response = api_response.to_dict()
            return finter.to_dataframe(response['cm'], response['column_types'])
        except ApiException as e:
            logger.error("Exception when calling AlphaApi->alpha_base_alpha_cm_retrieve: %s\n" % e)
        return
