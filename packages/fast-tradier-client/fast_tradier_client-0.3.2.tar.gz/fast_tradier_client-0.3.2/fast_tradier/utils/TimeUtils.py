from datetime import datetime, date, timedelta
from typing import Optional
import pandas as pd
import pytz

US_Eastern_TZ = pytz.timezone('US/Eastern')
YMD_Format = "%Y-%m-%d"
YYYYMDHHMM_Format = "YYYY-M-D HH:mm"
YMDHMS_Format = "%Y-%m-%d %H:%M:%S"

class TimeUtils:

    @staticmethod
    def convert_unix_ts(ts: int, tz: pytz.timezone = US_Eastern_TZ) -> Optional[datetime]:
        '''convert unix timestamp to datetime with the given timezone, US East by default'''
        if ts is None:
            return None

        if isinstance(ts, pd.Timestamp):
            ts = ts.to_pydatetime().timestamp()

        while ts > 1e10:
            ts = ts/1000
        return datetime.fromtimestamp(ts, tz)

    @staticmethod
    def us_east_now() -> datetime:
        return datetime.now().astimezone(US_Eastern_TZ)

    @staticmethod
    def parse_day_str(date_str: str, timezone: pytz.timezone = US_Eastern_TZ) -> date:
        """Parse a date string to date object in the intended timezone (US Eastern default).
        example input: '2023-12-10'
        """
        day_dt:datetime = datetime.strptime(date_str, YMD_Format).astimezone(timezone)
        return day_dt.date()
    
    @staticmethod
    def today_date(timezone: pytz.timezone = US_Eastern_TZ) -> date:
        today = datetime.now().astimezone(timezone)
        return today.date()
    
    @staticmethod
    def past_date(days_ago: int, timezone: pytz.timezone = US_Eastern_TZ) -> date:
        """Get a past date x days before today's date."""
        today_dt = TimeUtils.today_date(timezone)
        days_ago = days_ago if days_ago > 0 else days_ago
        past_dt = today_dt + timedelta(days=-days_ago)
        return past_dt

    @staticmethod
    def today_str(timezone: pytz.timezone = US_Eastern_TZ) -> str:
        today_dt = TimeUtils.today_date(timezone)
        return today_dt.strftime(YMD_Format)
        