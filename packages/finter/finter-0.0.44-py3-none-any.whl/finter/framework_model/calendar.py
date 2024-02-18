from __future__ import print_function

from datetime import datetime
from typing import Iterator, Dict

from finter.rest import ApiException

import finter
from finter.settings import api_client, logger

api_instance = finter.CalendarApi(api_client)


def iter_days(start: datetime.date, end: datetime.date, exchange="krx", date_type=1) -> Iterator[datetime]:
    """
    return iter days
    :param start: datetime.date
    :param end: datetime.date
    :param date_type: int | 0:all day 1: trading day, 2: closed day, 3: weekends (optional, default: 0)
    :param exchange: str |  'krx', 'us' (optional)
    """

    try:
        api_response = api_instance.calendar_retrieve(start_date=start.strftime("%Y%m%d"),
                                                      end_date=end.strftime("%Y%m%d"),
                                                      exchange=exchange, date_type=date_type)
        return iter([datetime.strptime(str(d_int), "%Y%m%d") for d_int in api_response.dates])

    except ApiException as e:
        logger.error("Exception when calling CalendarApi->calendar_retrieve: %s\n" % e)


def iter_trading_days(start, end, exchange='krx'):
    return iter_days(start, end, exchange=exchange, date_type=1)
