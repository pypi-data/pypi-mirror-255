#:coding=utf-8:

import time
import calendar
from datetime import datetime, date

__all__ = ('utc_to_local', 'local_to_utc', 'parse_utc_isostring')

def utc_to_local(utc_datetime):
    """
    UTC datetime/date obj => local datetime/date obj
    """
    if isinstance(utc_datetime, datetime):
        return datetime(*time.localtime(calendar.timegm(utc_datetime.timetuple()))[:6])
    elif isinstance(utc_datetime, date):
        return date(*time.localtime(calendar.timegm(utc_datetime.timetuple()))[:6])
    else:
        raise ValueError('Unknown datetime type!') 

def local_to_utc(local_datetime):
    """
    Local datetime/date obj => UTC datetime/date obj
    """
    if isinstance(local_datetime, datetime):
        return datetime(*time.gmtime(time.mktime(local_datetime.timetuple()))[:6])
    elif isinstance(local_datetime, date):
        return date(*time.gmtime(time.mktime(local_datetime.timetuple()))[:3])
    else:
        raise ValueError('Unknown datetime type!') 

def parse_utc_isostring(iso_string):
    # Ignore timezone because we assume it's UTC
    # Also don't bother with microseconds
    if not iso_string:
        return None
    if '.' in iso_string:
        iso_string = iso_string.split('.')[0]
    if 'Z' in iso_string:
        iso_string = iso_string.split('Z')[0]
    return datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%S")
