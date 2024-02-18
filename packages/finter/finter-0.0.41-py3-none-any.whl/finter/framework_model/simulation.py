from __future__ import print_function

import finter
from finter.settings import api_client
from finter.rest import ApiException
from finter.utils.convert import get_json_with_columns_from_dataframe

api_instance = finter.SimulationApi(api_client)


def adj_stat_container_helper(**kwargs):
    if 'position' in kwargs:
        kwargs['position'], kwargs['position_column_types'] = get_json_with_columns_from_dataframe(kwargs['position'])
    body = finter.SimulationRequest(**kwargs)  # SimulationRequest |

    try:
        api_response = api_instance.simulation_create(body)
        return api_response.result
    except ApiException as e:
        print("Exception when calling SimulationApi->simulation_create: %s\n" % e)
