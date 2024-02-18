from __future__ import annotations

import os
import re
import sys
from io import IOBase
from pathlib import Path
from typing import Any, Callable, Iterable
from configparser import _UNSET
from urllib.parse import urlparse
from ..text import build_netloc


def normalize_inout(inout: str|Path|IOBase|None, *, dir: str|Path|None = None, **kwargs) -> str|IOBase:
    if inout == 'stdout' or inout == sys.stdout or inout is None:
        return sys.stdout
    elif inout == 'stderr' or inout == sys.stderr:
        return sys.stderr
    elif inout == 'stdin' or inout == sys.stdin:
        return sys.stdin
    elif inout == False:
        return os.devnull
    elif isinstance(inout, IOBase):
        return inout
    elif isinstance(inout, str) and '://' in inout:
        # if this is an URL, remove the password
        # (handling the connection must therefore be done BEFORE calling normalize_inout)
        r = urlparse(inout)
        if r.password:
            netloc = build_netloc(hostname=r.hostname, port=r.port, username=r.username, password='***')
            r = r._replace(netloc=netloc)
        return r.geturl()
    elif isinstance(inout, (str,Path)):
        inout = str(inout).format(**kwargs)
        if dir and not ':' in inout and not inout.startswith('.'):
            inout = os.path.join(str(dir), inout)
        return os.path.expanduser(inout)
    else:
        raise ValueError(f'invalid inout type: {type(inout)}')


def get_inout_name(inout: str|Path|IOBase|None) -> str:
    if inout == 'stdout' or inout == sys.stdout or inout is None:
        return '<stdout>' if sys.stdout.isatty() else '<redirected stdout>'
    elif inout == 'stderr' or inout == sys.stderr:
        return '<stderr>' if sys.stderr.isatty() else '<redirected stderr>'
    elif inout == 'stdin' or inout == sys.stdin:
        return '<stdin>' if sys.stdin.isatty() else '<piped stdin>'
    elif inout == False:
        return '<devnull>'
    elif isinstance(inout, IOBase):
        return get_iobase_name(inout)
    elif isinstance(inout, (str,Path)):
        return inout
    else:
        raise ValueError(f'invalid inout type: {type(inout)}')


def get_iobase_name(out: IOBase) -> str:
    try:
        name = out.name
        if not name or not isinstance(name, str):
            name = None
    except AttributeError:
        name = None

    if name:
        if name.startswith('<') and name.endswith('>'):
            return name
        else:
            return f'<{name}>'

    else:
        return f"<{type(out).__name__}>"



def is_excel_path(path: str|Path, accept_table_suffix = False):
    if isinstance(path, Path):
        path = str(path)
    elif not isinstance(path, str):
        raise ValueError(f'invalid path type: {type(path)}')
    
    return re.search(r'\.xlsx(?:#[^\.]+)?$' if accept_table_suffix else r'\.xlsx$', path, re.IGNORECASE)


def split_excel_path(path: str|Path, default_table_name: str = None, **kwargs) -> tuple[Path,str]:
    """ Return (actual path, table name) """
    if isinstance(path, Path):
        path = str(path)
    elif not isinstance(path, str):
        raise ValueError(f'invalid path type: {type(path)}')
        
    path = path.format(**kwargs)

    m = re.match(r'^(.+\.xlsx)(?:#([^\.]*))?$', path, re.IGNORECASE)
    if not m:
        return (Path(path), default_table_name)
    
    return (Path(m[1]), m[2] if m[2] else default_table_name)


class Row:
    """
    A row of tabular data with known headers.

    May be initialized with:
    - _a getter function_: in this case, values are read only once (when the Row object is accessed for the first time).
    - _actual values_.
    """
    def __init__(self, get: Iterable|Callable[[int],Any], *, headers: list[str], index: int, set: Callable[[int,Any]] = None):
        if callable(get):
            self._values = None
            self._values_mustget: dict[int,bool] = None
            self._get = get
            self._set = set
        else:
            # "get" contains actual values
            self._values = get if isinstance(get, list) else list(get)
            self._values_mustget: dict[int,bool] = None
            self._get = None
            self._set = set

        self.headers = headers
        self.index = index
        self._header_indexes: dict[str,int] = None
        
        
    def __len__(self):
        return len(self.headers)


    @property
    def values(self) -> list[Any]:
        if self._values is None:
            self._values = [self._get(index) for index in range(0, len(self.headers))]
            self._values_mustget = None

        elif self._values_mustget:
            for index in range(0, len(self.headers)):
                if self._values_mustget[index]:
                    self._values[index] = self._get(index)
            self._values_mustget = None
        
        return self._values


    def __getitem__(self, key: int|str):
        if not isinstance(key, int):
            key = self._get_header_index(key)
            
        if self._values is None:
            self._values = [ _UNSET ] * len(self.headers)
            self._values_mustget = {index: True for index in range(0, len(self.headers))}

            value = self._get(key)
            self._values[key] = value
            self._values_mustget[key] = False
            return value

        elif self._values_mustget and self._values_mustget[key]:
            value = self._get(key)
            self._values[key] = value
            self._values_mustget[key] = False
            return value

        else:
            return self._values[key]
        

    def __setitem__(self, key: int|str, value):
        if not isinstance(key, int):
            key = self._get_header_index(key)

        if self._values is None:
            self._values = [ _UNSET ] * len(self.headers)
            self._values_mustget = {index: True for index in range(0, len(self.headers))}

        self._values[key] = value
        if self._values_mustget is not None:
            self._values_mustget[key] = False
        
        if self._set:
            self._set(key, value)


    def _get_header_index(self, header: str):
        if self._header_indexes is None:
            if not self.headers:
                raise ValueError(f"cannot use string keys (no headers)")
            self._header_indexes = {header: i for i, header in enumerate(self.headers)}
        return self._header_indexes[header]


    def as_dict(self):
        return {header: self[i] for i, header in enumerate(self.headers)}
