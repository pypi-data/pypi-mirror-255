from __future__ import annotations
from typing import TypeVar
from datetime import datetime, time, timedelta, timezone, tzinfo

T_WithTime = TypeVar('T_WithTime', datetime, time)


def is_aware(value: T_WithTime):
    # See: https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
    if value is None:
        return False
    return value.tzinfo is not None and value.utcoffset() is not None


def now_aware(tz: tzinfo = None, *, ms = True):
    """
    Get the current datetime in the timezone `tz` (use `tz=None` or `tz='local'` for the system local timezone).
    """
    now = datetime.now().astimezone(None if tz == 'local' else (timezone.utc if tz == 'utc' else tz))
    if not ms:
        now = now.replace(microsecond=0)
    return now


def make_aware(value: T_WithTime, tz: tzinfo = None) -> T_WithTime:
    """
    Make a datetime aware in timezone `tz` (use `tz=None` or `tz='local'` for the system local timezone).
    """
    if value is None:
        return None
    if is_aware(value):
        raise ValueError(f"already aware: {value}")
    
    if not tz or tz == 'local':
        try:
            from tzlocal import get_localzone
            tz = get_localzone()
        except ImportError:
            raise ValueError(f"tzlocal not available")

    return value.replace(tzinfo=timezone.utc if tz == 'utc' else tz)


def make_naive(value: T_WithTime, tz: tzinfo = None) -> T_WithTime:
    """
    Make a datetime naive and expressed in timezone `tz` (use `tz=None` or `tz='local'` for the system local timezone).
    """
    if value is None:
        return None
    if not is_aware(value):
        raise ValueError(f"already naive: {value}")

    value = value.astimezone(None if tz == 'local' else (timezone.utc if tz == 'utc' else tz))
    value = value.replace(tzinfo=None)
    return value


def duration_iso_string(duration: timedelta):
    # Adapted from: django.utils.duration.duration_iso_string
    if duration < timedelta(0):
        sign = "-"
        duration *= -1
    else:
        sign = ""

    days, hours, minutes, seconds, microseconds = _get_duration_components(duration)
    ms = ".{:06d}".format(microseconds) if microseconds else ""
    return "{}P{}DT{:02d}H{:02d}M{:02d}{}S".format(
        sign, days, hours, minutes, seconds, ms
    )


def _get_duration_components(duration: timedelta):
    days = duration.days
    seconds = duration.seconds
    microseconds = duration.microseconds

    minutes = seconds // 60
    seconds = seconds % 60

    hours = minutes // 60
    minutes = minutes % 60

    return days, hours, minutes, seconds, microseconds

