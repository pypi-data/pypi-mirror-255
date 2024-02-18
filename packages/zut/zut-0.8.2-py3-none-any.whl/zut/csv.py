from __future__ import annotations
import csv
from io import IOBase
import os
from typing import Any, Callable, Iterable

from .text import skip_utf8_bom
from .format import Format
from . import files


def dump_to_csv(target: IOBase|os.PathLike, data: Iterable[Iterable|dict], headers: list = None, encoding: str = 'utf-8-sig', delimiter: str = None, quotechar: str = None, nullval: str = None, decimal_separator: str = None):
    """
    Dump a list of dicts or iterables to CSV.
    """
    from .inout import OutCsv

    with OutCsv(target, headers=headers, encoding=encoding, delimiter=delimiter, quotechar=quotechar, nullval=nullval, decimal_separator=decimal_separator) as o:
        for row in data:
            o.append(row)


def load_from_csv(source: IOBase|os.PathLike, conversions: dict[str,type|Callable] = None, encoding: str = 'utf-8', delimiter: str = None, quotechar: str = None, nullval: str = None):
    """
    Load a list of dicts from CSV.
    """
    from .inout import InCsv

    with InCsv(source, conversions=conversions, encoding=encoding, delimiter=delimiter, quotechar=quotechar, nullval=nullval) as i:
        return [row.as_dict() for row in i]


def get_csv_headers(csv_file: os.PathLike|IOBase, encoding: str = 'utf-8', *, delimiter: str = None, quotechar: str = None, nullval: str = None) -> list[str]:        
    fp = None
    fp_to_close = None

    delimiter, quotechar, nullval = Format.apply_csv_defaults(delimiter, quotechar, nullval)

    try:        
        if isinstance(csv_file, IOBase):
            fp = csv_file
            fp.seek(0)
        else:
            fp = files.open(csv_file, 'r', newline='', encoding=encoding)
            fp_to_close = fp
            if encoding == 'utf-8':
                skip_utf8_bom(fp)
            
        reader = csv.reader(fp, delimiter=delimiter, quotechar=quotechar)
        try:
            return [(None if value == nullval else value) for value in next(reader)]
        except StopIteration:
            return None

    finally:
        if fp_to_close:
            fp_to_close.close()
        elif fp:
            fp.seek(0)


def get_csv_dict_list(csv_file: os.PathLike|IOBase, encoding: str = 'utf-8', *, delimiter: str = None, quotechar: str = None, nullval: str = None) -> list[dict[str,Any]]:        
    fp = None
    fp_to_close = None

    delimiter, quotechar, nullval = Format.apply_csv_defaults(delimiter, quotechar, nullval)

    try:        
        if isinstance(csv_file, IOBase):
            fp = csv_file
            fp.seek(0)
        else:
            fp = files.open(csv_file, 'r', newline='', encoding=encoding)
            fp_to_close = fp
            if encoding == 'utf-8':
                skip_utf8_bom(fp)
            
        reader = csv.reader(fp, delimiter=delimiter, quotechar=quotechar)
        headers: list[str] = None
        data_list: list[dict[str,Any]] = []

        for row in reader:
            if headers is None:
                headers = [None if value == nullval else value for value in row]
                continue
            data = {headers[i]: None if value == nullval else value for i, value in enumerate(row)}
            data_list.append(data)

        return data_list

    finally:
        if fp_to_close:
            fp_to_close.close()
        elif fp:
            fp.seek(0)
