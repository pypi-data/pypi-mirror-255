import pandas as pd
from datetime import datetime


def outsample_end_date(now: datetime, n_week=104, n_seconds=None) -> datetime:
    if n_seconds is not None and n_seconds >= 0:
        return now - pd.Timedelta(seconds=n_seconds)
    return pd.date_range(end=now, periods=n_week, freq="1W-SAT")[0].to_pydatetime()
