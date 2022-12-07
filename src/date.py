import pandas as pd
from datetime import datetime, timedelta, timezone


class Date:

    @staticmethod
    def now(timezone_selected=timezone.utc):
        return pd.to_datetime(datetime.now(timezone_selected))

    @staticmethod
    def formatted(datetime_selected=datetime.now(timezone.utc), date_format="%Y-%m-%d %H:%M:%S"):
        datetime_selected = datetime_selected.replace(tzinfo=timezone.utc)
        return datetime_selected.strftime(date_format)
