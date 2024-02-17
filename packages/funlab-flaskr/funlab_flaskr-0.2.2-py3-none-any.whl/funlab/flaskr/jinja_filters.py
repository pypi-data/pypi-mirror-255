
from datetime import date, datetime, time, timedelta
from enum import Enum
import math
from funlab.utils import dtts

__all__ = ['timestamp_natation', 'common_formatter']

def timestamp_natation(timestamp:float, formatstr:str='%Y-%m-%d %H:%M:%S'):
    """
    formatstr 為python strftime 的 format code,
    為提供季度表示法, 例如: 2021-01-01 00:00:00 -> 2021Q1增為一 加 %q 做為季度值, formatstr = %YQ%q
    將timestamp轉為月表示法, 例如: 2021-01-01 00:00:00 -> 2021M1, formatstr = %YM%m
    """
    ddate = dtts.utc_timestamp2local_datetime(timestamp)
    formatstr = formatstr.replace('%q', f'{ddate.month//3+1}')
    notation = ddate.strftime(formatstr)
    return notation

def common_formatter(value):
    """通用的formatter"""
    if isinstance(value, float):
        try:
            if value == (int(value)):
                return f'{value:,}'
            else:
                return f'{value:,.3f}'
        except Exception: # OverflowError: 'nan', 'inf'
                return str(value)
    elif isinstance(value, int):
        return f'{value:,}'
    elif isinstance(value, Enum):
        return value.name
    elif isinstance(value, (datetime, date,)):
        if isinstance(value, datetime) and value - datetime.combine(value.date(), time(0, 0, 0)) == timedelta(0):
            value = value.date()
        return value.isoformat()
    # elif isinstance(value, pd.Timestamp):  暫不import & 處理 pandas.Timestamp type
    #     return value.isoformat()
    elif value is None:
        return 'NA'
    else:
        return str(value)