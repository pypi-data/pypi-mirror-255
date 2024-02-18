from __future__ import annotations

import logging
import sys
from datetime import tzinfo
from io import IOBase
from pathlib import Path
from typing import Any, Callable

from ..text import slugify
from .InDb import InDb
from .InCsv import InCsv
from .InExcel import InExcel
from .InTable import InTable
from .OutDb import OutDb
from .OutCsv import OutCsv
from .OutExcel import OutExcel
from .OutFile import OutFile
from .OutTable import OutTable
from .OutTabulate import OutTabulate
from .utils import Row, is_excel_path, split_excel_path, normalize_inout  # NOTE: kept even if not used, so that these names are available from zut root

logger = logging.getLogger(__name__)


def out_file(out: str|Path|IOBase|None = None, *, dir: str|Path|None = None, title: str|None = None, append: bool = False, encoding: str = 'utf-8-sig', newline: str = None, atexit: bool|Callable = None, **kwargs) -> OutFile:
    clazz: OutFile = None
    for handler in _out_file_handler:
        a_clazz = handler(out)
        if a_clazz:
            clazz = a_clazz
            break

    if not clazz:
        clazz = OutFile
    elif not isinstance(clazz, type) or not issubclass(clazz, OutFile):
        raise ValueError(f"invalid handler class: {clazz}")
    
    return clazz(out, dir=dir, title=title, append=append, encoding=encoding, newline=newline, atexit=atexit, **kwargs)


def out_table(out: Path|str|IOBase|None = None, *, dir: str|Path|None = None, title: str|None = None, append: bool = False, encoding: str = 'utf-8-sig', headers: list[str] = None, delimiter: str = None, quotechar: str = None, nullval: str = None, tz: tzinfo = None, decimal_separator: str = None, atexit: bool|Callable = '__if_excel__', **kwargs) -> OutTable:
    clazz: OutTable = None
    for handler in _out_table_handler:
        a_clazz = handler(out)
        if a_clazz:
            clazz = a_clazz
            break
    
    if not clazz:
        if OutTabulate.is_available() and (out is None or out in ['tabulate', 'tab', 't']):
            clazz = OutTabulate
            out = None
        elif isinstance(out, str) and out.startswith(('postgresql:', 'postgres:', 'pg:', 'mssql:')):
            clazz = OutDb
        elif isinstance(out, (str,Path)) and is_excel_path(out, accept_table_suffix=True):
            clazz = OutExcel
        else:
            clazz = OutCsv
    elif not isinstance(clazz, type) or not issubclass(clazz, OutTable):
        raise ValueError(f"invalid handler class: {clazz}")

    return clazz(out, dir=dir, title=title, append=append, encoding=encoding, headers=headers, delimiter=delimiter, tz=tz, decimal_separator=decimal_separator, quotechar=quotechar, nullval=nullval, atexit=atexit, **kwargs)


def in_table(src: Path|str|IOBase, query: str = None, *args, dir: str|Path|None = None, title: str|None = None, encoding: str = 'utf-8', delimiter: str = None, quotechar: str = None, nullval: str = None, conversions: dict[int|str,type|Callable] = None, debug: bool = False, offset: int = None, limit: int = None, **kwargs) -> InTable:
    clazz: InTable = None
    for handler in _in_table_handler:
        a_clazz = handler(src)
        if a_clazz:
            clazz = a_clazz
            break
        
    if not clazz:
        if isinstance(src, str) and src.startswith(('postgresql:', 'postgres:', 'pg:', 'mssql:')):
            clazz = InDb
        elif isinstance(src, (str,Path)) and is_excel_path(src, accept_table_suffix=True):
            clazz = InExcel
        else:
            clazz = InCsv
    elif not isinstance(clazz, type) or not issubclass(clazz, InTable):
        raise ValueError(f"invalid handler class: {clazz}")
    
    return clazz(src, query=query, *args, dir=dir, title=title, encoding=encoding, delimiter=delimiter, quotechar=quotechar, nullval=nullval, conversions=conversions, debug=debug, offset=offset, limit=limit, **kwargs)


def transfer_table(src: Path|str|IOBase, out: str|Path|IOBase, *, conversions: dict[int|str,type|Callable] = None, headers: list[str]|dict[str, Any] = None, dir: str|Path|None = None, append: bool = False, encoding: str = 'utf-8', delimiter: str = None, quotechar: str = None, nullval: str = None, **kwargs):
    """
    - `conversions`: conversions to apply to source values. Keys are source headers.
    - `headers`: target headers, or mapping (`dict`): keys are target headers, values are source headers (`str`) or value (`str` prefixed with `value:` or other types). Use '*' as key and value to include non-mentionned source headers without modifications.
    """
    class RowIndex:
        def __init__(self, index: int):
            self.index = index

        def __repr__(self):
            return f"[{self.index}]"
        

    with in_table(src, dir=dir, conversions=conversions, encoding=encoding, delimiter=delimiter, quotechar=quotechar, nullval=nullval, **kwargs) as _src_table:
        # Read/write headers and build mapping
        if headers:
            out_headers = []
            row_transform_needed = True
            out_row_model = []

            default_spec = ('*' if '*' in headers else None) if isinstance(headers, list) else headers.pop('*', None)
            if default_spec:
                for src_index, src_header in enumerate(_src_table.headers):
                    if default_spec == 'slugify':
                        target_header = slugify(src_header)
                    elif default_spec.startswith('slugify:'):
                        target_header = slugify(src_header, separator=default_spec[len('slugify:'):])
                    else:
                        target_header = src_header

                    out_headers.append(target_header)
                    out_row_model.append(RowIndex(src_index))
        

            for target_header, spec in ([(header, header) for header in headers] if isinstance(headers, list) else headers.items()):
                if isinstance(spec, str):
                    if spec.startswith('value:'):
                        spec = spec[len('value:'):]
                    else:
                        try:
                            src_index = _src_table.headers.index(spec)
                        except ValueError:
                            raise ValueError(f"header \"{spec}\" (for mapping to \"{target_header}\") not found in CSV file")
                        spec = RowIndex(src_index)
                else:
                    spec = spec

                try:
                    out_index = out_headers.index(target_header)
                    out_row_model[out_index] = spec
                except ValueError:
                    out_headers.append(target_header)
                    out_row_model.append(spec)
        else:
            out_headers = _src_table.headers
            row_transform_needed = False

        # Read/write rows
        with out_table(out, dir=dir, headers=out_headers, append=append, encoding=encoding, delimiter=delimiter, quotechar=quotechar, nullval=nullval, **kwargs) as _out_table:
            for src_row in _src_table:
                if row_transform_needed:
                    out_row = []

                    for spec in out_row_model:
                        if isinstance(spec, RowIndex):
                            value = src_row[spec.index]
                        else:
                            value = spec
                        out_row.append(value)
                else:
                    out_row = src_row.values

                _out_table.append(out_row)


_out_file_handler: list[Callable[[Any], type[OutFile]|None]] = []
_out_table_handler: list[Callable[[Any], type[OutTable]|None]] = []
_in_table_handler: list[Callable[[Any], type[InTable]|None]] = []

def register_out_file_handler(handler: Callable[[Any], type[OutFile]|None]):
    _out_file_handler.append(handler)
    
def register_out_table_handler(handler: Callable[[Any], type[OutTable]|None]):
    _out_table_handler.append(handler)
    
def register_in_table_handler(handler: Callable[[Any], type[InTable]|None]):
    _in_table_handler.append(handler)
