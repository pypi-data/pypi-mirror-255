from __future__ import annotations
import re
import unicodedata
from io import BufferedIOBase, TextIOWrapper
from typing import Generic, Iterable, TypeVar
from urllib.parse import quote, urlencode, urlparse, urlunparse
from ipaddress import AddressValueError, IPv4Address, IPv6Address, ip_address
from uuid import UUID


T = TypeVar('T')

class ValueString(str, Generic[T]):
    """
    A string internally associated to a value of a given type.
    """
    value: T

    def __new__(cls, strvalue: str, value: T):
        hb = super().__new__(cls, strvalue)
        hb.value = value
        return hb


def slugify(value: str, separator: str = '-', keep: str = None, strip_separator: bool = True, strip_keep: bool = True, if_none: str = None) -> str:
    """ 
    Generate a slug.
    """
    if value is None:
        return if_none
    
    separator = separator if separator is not None else ''
    keep = keep if keep is not None else ''

    # Normalize the string: replace diacritics by standard characters, lower the string, etc
    value = str(value)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower()

    # Remove special characters
    remove_sequence = r'^a-zA-Z0-9\s' + re.escape(separator) + re.escape(keep)
    value = re.sub(f"[{remove_sequence}]", "", value)

    # Replace spaces and successive separators by a single separator
    replace_sequence = r'\s' + re.escape(separator)
    value = re.sub(f"[{replace_sequence}]+", separator, value)
    
    # Strips separator and kept characters
    strip_chars = (separator if strip_separator else '') + (keep if strip_keep else '')
    value = value.strip(strip_chars)

    return value


def slugify_django(value: str) -> str:
    """ 
    Generate a slug, same as `django.utils.text.slugify`.
    """
    return slugify(value, separator='-', keep='_', strip_separator=True, strip_keep=True, if_none='none')


def slugify_snake(value: str, separator: str = '_', if_none: str = None) -> str:
    """
    CamèlCase => camel_case
    """
    if value is None:
        return if_none
    
    separator = separator if separator is not None else ''
    
    # Normalize the string: replace diacritics by standard characters, etc
    # NOTE: don't lower the string
    value = str(value)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[-_\s]+", separator, value).strip(separator)
    value = re.sub(r'(.)([A-Z][a-z]+)', f'\\1{separator}\\2', value)
    return re.sub(r'([a-z0-9])([A-Z])', f'\\1{separator}\\2', value).lower()


def remove_consecutive_whitespaces(s: str):
    if s is None:
        return None
    return re.sub(r'\s+', ' ', s).strip()


def remove_whitespaces(s):
    if s is None:
        return None
    return re.sub(r'\s', '', s)


def skip_utf8_bom(fp: TextIOWrapper|BufferedIOBase):
    """
    Skip UTF8 byte order mark, if any.
    """
    data = fp.read(1)
    
    if isinstance(data, str): # text mode
        if len(data) >= 1 and data[0] == UTF8_BOM:
            return True
        
    elif isinstance(data, bytes): # binary mode
        if len(data) >= 1 and data[0] == UTF8_BOM_BINARY[0]:
            data += fp.read(2)
            if data[0:3] == UTF8_BOM_BINARY:
                return True
    
    fp.seek(0)
    return False


UTF8_BOM = '\ufeff'
UTF8_BOM_BINARY = UTF8_BOM.encode('utf-8')


def build_url(*, scheme: str = '', hostname: str|IPv4Address|IPv6Address = None, port: int = None, username: str = None, password: str = None, path: str = None, params: str = None, query: str = None, fragment: str = None, noquote = False, hide_password = False):
    netloc = build_netloc(hostname=hostname, port=port, username=username, password=password, noquote=noquote, hide_password=hide_password)

    if noquote:
        actual_query = query
    else:
        if isinstance(query, dict):
            actual_query = urlencode(query)
        elif isinstance(query, list):
            named_parts = []
            unnamed_parts = []
            for part in query:
                if isinstance(part, tuple):
                    named_parts.append(part)
                else:
                    unnamed_parts.append(part)
            actual_query = urlencode(named_parts, quote_via=quote)
            actual_query += ('&' if actual_query else '') + '&'.join(quote(part) for part in unnamed_parts)
        else:
            actual_query = query

    return urlunparse((scheme or '', netloc or '', (path or '') if noquote else quote(path or ''), (params or '') if noquote else quote(params or ''), actual_query or '', (fragment or '') if noquote else quote(fragment or '')))


def build_netloc(*, hostname: str|IPv4Address|IPv6Address = None, port: int = None, username: str = None, password: str = None, noquote = False, hide_password = False):
    netloc = ''
    if username or hostname:
        if username:
            netloc += username if noquote else quote(username)
            if password:
                netloc += ':' + ('***' if hide_password else (password if noquote else quote(password)))
            netloc += '@'

        if hostname:
            if isinstance(hostname, IPv4Address):
                netloc += hostname.compressed
            elif isinstance(hostname, IPv6Address):
                netloc += f"[{hostname.compressed}]"
            else:
                ipv6 = None
                if ':' in hostname:
                    try:
                        ipv6 = IPv6Address(hostname)
                    except AddressValueError:
                        pass

                if ipv6:
                    netloc += f"[{ipv6.compressed}]"
                else:
                    netloc += hostname if noquote else quote(hostname)

            if port:
                if not isinstance(port, int):
                    raise ValueError(f"invalid type for port: {type(port)}")
                netloc += f':{port}'

    return netloc


def hide_url_password(url: str):
    r = urlparse(url)
    return build_url(scheme=r.scheme, hostname=r.hostname, port=r.port, username=r.username, password=r.password, path=r.path, params=r.params, query=r.query, fragment=r.fragment, noquote=True, hide_password=True)


def merge_ip_addresses(*args: str|None) -> list[str]:
    """
    Merge standardized ip addresses.

    Typical usage: `ips = merge_ip_addresses(request.META.get('HTTP_X_FORWARDED_FOR'), request.META.get('REMOTE_ADDR'))`    
    """
    ips = []
    for arg in args:
        if arg:
            for ip_str in arg.split(','):
                ip_str = ip_str.strip()
                if ip_str:
                    m = _ENCLOSED_IP_PATTERN.match(ip_str)
                    if m:
                        ip_str = m[1]

                    try:
                        ip = ip_address(ip_str).compressed
                    except ValueError:
                        ip = ip_str

                    if not ip in ips:
                        ips.append(ip)

    return ips

_ENCLOSED_IP_PATTERN = re.compile(r'^\[([0-9a-f\:\.]+)\](?:\:\d+)?$', re.IGNORECASE)


def is_valid_uuid(uuid: str, version=4):
    """
    Check if the given string is a valid UUID.
    """    
    try:
        uuid_obj = UUID(uuid, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid


class Filter:
    def __init__(self, spec: str|re.Pattern, normalize: bool = False):
        self.normalize = normalize

        if isinstance(spec, re.Pattern):
            self.regex = spec

        elif isinstance(spec, str) and spec.startswith('^'):
            m = re.match(r'^(.*\$)(A|I|L|U|M|S|X)+$', spec, re.IGNORECASE)
            if m:
                pattern = m[1]
                flags = re.NOFLAG
                for letter in m[2]:
                    flags |= re.RegexFlag[letter.upper()]
            else:
                pattern = spec
                flags = re.NOFLAG

            self.regex = re.compile(pattern, flags)

        elif isinstance(spec, str):
            if self.normalize:
                spec = self.normalize_spec(spec)

            if '*' in spec:
                name_parts = spec.split('*')
                pattern_parts = [re.escape(name_part) for name_part in name_parts]
                pattern = r'^' + r'.*'.join(pattern_parts) + r'$'
                self.regex = re.compile(pattern)
            else:
                self.regex = spec

        else:
            raise TypeError(f"filter spec must be a string or regex pattern, got {type(spec).__name__}")
       

    def __repr__(self) -> str:
        return self.regex.pattern if isinstance(self.regex, re.Pattern) else self.regex


    def matches(self, value: str, is_normalized: bool = False):
        if value is None:
            value = ""
        elif not isinstance(value, str):
            value = str(value)

        if self.normalize and not is_normalized:
            value = self.normalize_value(value)

        if isinstance(self.regex, re.Pattern):
            if self.regex.match(value):
                return True
            
        elif self.regex == value:
            return True


    @classmethod
    def normalize_spec(cls, spec: str):
        return slugify(spec, separator=None, keep='*', strip_keep=False, if_none=None)
    
    
    @classmethod
    def normalize_value(cls, value: str):
        return slugify(value, separator=None, keep=None, if_none=None)


class Filters:
    def __init__(self, specs: list[str|re.Pattern]|str|re.Pattern, normalize: bool = False):
        self.filters: list[Filter] = []

        if specs:
            if isinstance(specs, (str,re.Pattern)):
                specs = [specs]

            for spec in specs:
                self.filters.append(Filter(spec, normalize=normalize))


    def __len__(self):
        return len(self.filters)


    def matches(self, value: str, if_no_filter: bool = False):
        if not self.filters:
            return if_no_filter
        
        if value is None:
            value = ""
        elif not isinstance(value, str):
            value = str(value)
        
        normalized_value = None    

        for str_filter in self.filters:
            if str_filter.normalize:
                if normalized_value is None:
                    normalized_value = Filter.normalize_value(value)
                if str_filter.matches(normalized_value, is_normalized=True):
                    return True
            else:
                if str_filter.matches(value):
                    return True
                
        return False
