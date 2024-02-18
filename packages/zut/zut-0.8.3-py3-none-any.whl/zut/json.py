from __future__ import annotations
import json
import re
from datetime import datetime, time, date, timedelta
from decimal import Decimal
from uuid import UUID
from enum import Enum, Flag
from .datetime import is_aware, duration_iso_string

try:
    from django.utils.functional import Promise
    with_django = True
except ImportError:
    with_django = False


class ExtendedJSONEncoder(json.JSONEncoder):
    """
    Adapted from: django.core.serializers.json.DjangoJSONEncoder
    Usage example: json.dumps(data, indent=4, cls=ExtendedJSONEncoder)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def default(self, o):
        if isinstance(o, datetime):
            r = o.isoformat()
            if o.microsecond and o.microsecond % 1000 == 0:
                r = r[:23] + r[26:]
            if r.endswith("+00:00"):
                r = r[:-6] + "Z"
            return r
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond and o.microsecond % 1000 == 0:
                r = r[:12]
            return f'T{r}'
        elif isinstance(o, timedelta):
            return duration_iso_string(o)
        elif isinstance(o, (Decimal, UUID)):
            return str(o)
        elif with_django and isinstance(o, Promise):
            return str(o)
        elif isinstance(o, (Enum,Flag)):
            return o.name
        else:
            return super().default(o)


class ExtendedJSONDecoder(json.JSONDecoder):
    """
    Reverse of: ExtendedJSONEncoder.
    Usage example: json.loads(data, cls=ExtendedJSONDecoder)
    """
    def __init__(self, **kwargs):
        if not 'object_hook' in kwargs:
            kwargs['object_hook'] = extended_json_decode_hook
        super().__init__(**kwargs)


def extended_json_decode_hook(obj):
    """
    Decode date and datetime objects with ISO format.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = extended_json_decode_hook(value)

    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            obj[i] = extended_json_decode_hook(value)

    elif isinstance(obj, str):
        if len(obj) < 10:
            return obj # shortcut
        
        value = _decode_date(obj)
        if value:
            return value
        
        value = _decode_datetime(obj)
        if value:
            return value
        
        value = _decode_timedelta(obj)
        if value:
            return value
        
    return obj


def _decode_datetime(value: str) -> datetime|time|None:
    m = re.match(r'^(\d{4}-\d{2}-\d{2})?(T\d{2}:\d{2}:\d{2})(\.\d{3,6})?(Z|[\+\-]\d{2}:\d{2})?$', value)
    if not m:
        return None
    
    datepart = m.group(1) or '' # optional
    timepart = m.group(2) # mandatory
    microsecondpart = m.group(3) or '' # optional
    tz = m.group(4) or '' # optional

    format_string = ''

    if datepart:
        format_string += '%Y-%m-%d'
    
    format_string += 'T%H:%M:%S'
    
    if microsecondpart:
        format_string += '.%f'
    
    if tz:
        if not datepart:
            # invalid (timezone-aware time without date)
            return None
        
        format_string += '%z'
        # adapt timezone: replace 'Z' with +0000, or +XX:YY with +XXYY
        if tz == 'Z':
            tz = '+0000'
        else:
            tz = tz[:-3] + tz[-2:]
    
    try:
        result = datetime.strptime(f"{datepart}{timepart}{microsecondpart}{tz}", format_string)
    except ValueError: # example: invalid month, day, hour, etc
        return None

    if not datepart:
        result = result.time()
    return result


def _decode_timedelta(value: str) -> timedelta|None:
    m = re.match(r'^(\-)?P(\d+)DT(\d{2})H(\d{2})M(\d{2})(?:\.(\d{3,6}))?S$', value)
    if not m:
        return None
    
    sign = m.group(1) or ''
    days = int(m.group(2))
    hours = int(m.group(3))
    minutes = int(m.group(4))
    seconds = int(m.group(5))

    if m.group(6):
        microseconds = int(m.group(6).ljust(6, '0'))
    else:
        microseconds = 0

    if sign == '-':
        days *= -1
        hours *= -1
        minutes *= -1
        seconds *= -1
        microseconds *= -1

    try:
        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)
    except ValueError: # example: invalid month, day, hour, etc
        return None


def _decode_date(value: str) -> date|None:
    m = re.match(r'^\d{4}-\d{2}-\d{2}$', value)
    if not m:
        return None

    try:
        result = datetime.strptime(value, "%Y-%m-%d")
    except ValueError: # example: invalid month or day
        return None
    
    return result.date()
