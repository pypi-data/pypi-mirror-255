from __future__ import annotations
import locale
from decimal import Decimal, InvalidOperation
from .text import ValueString

def as_gib(value: int):
    """
    Convert from bytes to GigiBytes.
    """
    return value / 1024**3


def as_mib(value: int):
    """
    Convert from bytes to MegiBytes.
    """
    return value / 1024**2


def as_kib(value: int):
    """
    Convert from bytes to KiliBytes.
    """
    return value / 1024


def human_bytes(value: int, *, unit: str = 'iB', divider: int = 1024, decimals: int = 2, decimal_separator: str = None, thousands_separator: str = None, max_multiple: str = None):
    """
    Get a human-readable representation of a number of bytes.

    `max_multiple` may be `K`, `M`, `G'` or `T'. 
    """
    return human_number(value, unit=unit, divider=divider, decimals=decimals, decimal_separator=decimal_separator, thousands_separator=thousands_separator, max_multiple=max_multiple)


def human_number(value: int, *, unit: str = '', divider: int = 1000, decimals: int = 2, decimal_separator: str = None, thousands_separator: str = None, max_multiple: str = None):
    """
    Get a human-readable representation of a number.

    `max_multiple` may be `K`, `M`, `G'` or `T'. 
    """
    if value is None:
        return ValueString('', None)

    suffixes = []

    # Append non-multiple suffix (bytes)
    # (if unit is 'iB' we dont display the 'i' as it makes more sens to display "123 B" than "123 iB")
    if unit:
        suffixes.append(' ' + (unit[1:] if len(unit) >= 2 and unit[0] == 'i' else unit))
    else:
        suffixes.append('')

    # Append multiple suffixes
    for multiple in ['K', 'M', 'G', 'T']:
        suffixes.append(f' {multiple}{unit}')
        if max_multiple and max_multiple.upper() == multiple:
            break

    i = 0
    suffix = suffixes[i]
    divided_value = value

    while divided_value > 1000 and i < len(suffixes) - 1:
        divided_value /= divider
        i += 1
        suffix = suffixes[i]

    # Format value
    if i == 0:
        formatted_value = '{value:.0f}'.format(value=divided_value)
    else:
        formatted_value = ('{value:.'+str(decimals)+'f}').format(value=divided_value)

    #  Replace separators
    locale_params = locale.localeconv()
    if decimal_separator is None:
        decimal_separator = locale_params['decimal_point']
    if thousands_separator is None:
        thousands_separator = locale_params['thousands_sep']
    
    if decimal_separator != '.' or thousands_separator != '':
        try:
            sep = formatted_value.index('.')
            int_part = formatted_value[0:sep]
            dec_part = formatted_value[sep+1:]
        except:
            int_part = formatted_value
            dec_part = ''

        int_part = ('0' * (3 - len(int_part) % 3) if len(int_part) % 3 > 0 else '') + int_part
        int_part = thousands_separator.join([int_part[i:i+3] for i in range(0, len(int_part), 3)]).lstrip('0')

        formatted_value = int_part + decimal_separator + dec_part
    
    # Display formatted value with suffix
    return ValueString(f'{formatted_value}{suffix}', value)
