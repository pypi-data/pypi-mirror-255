from __future__ import annotations
import csv
import logging
import locale
from datetime import datetime, time
from decimal import Decimal
from io import IOBase
from pathlib import Path
from typing import Any, Iterable
from ..text import ValueString
from ..csv import get_csv_headers
from ..format import Format
from .. import files
from .OutTable import OutTable

logger = logging.getLogger(__name__)


class OutCsv(OutTable):
    file: IOBase
    
    def __init__(self, out: str|Path|IOBase|None = None, *, delimiter: str = None, quotechar: str = None, nullval: str = None, decimal_separator: str = None, **kwargs):
        self._delimiter, self._quotechar, self._nullval = Format.apply_csv_defaults(delimiter, quotechar, nullval)
        self._decimal_separator = locale.localeconv()['decimal_point'] if decimal_separator is None else decimal_separator

        self._writer: csv._writer = None

        super().__init__(out, newline='', **kwargs)


    # -------------------------------------------------------------------------
    # OutTable subclassing
    #
    
    def _get_existing_headers(self) -> list[str]|None:
        if not self._append:
            return []  # file will be truncated
        
        if not isinstance(self.out, str) or not files.exists(self.out):
            return []  # we consider output as a new file
        
        # From now on, we append to an existing file
        existing_headers = get_csv_headers(self.out, encoding=self._encoding, delimiter=self._delimiter, quotechar=self._quotechar, nullval=self._nullval)
        if existing_headers is None:
            return []  # existing file is empty
        
        return existing_headers


    def _export_new_headers(self, headers: list[str]):
        self._get_writer().writerow(headers)
        self.file.flush()


    def _add_new_header(self, header: str, index: int):
        # cannot modify existing headers (we don't modify existing file)
        logger.warning(f"header \"{header}\" not found in existing headers: values will be appended at column {index + 1} without a column title")


    def _export_prepared_row(self, row: Iterable):
        self._get_writer().writerow(row)
        self.file.flush()


    def _format_value(self, value: Any, index: int, depth: int = 0) -> Any:
        if isinstance(value, ValueString):
            # For CSV we want the actual value (we can still apply formatting when opening in Excel)
            # NOTE: we don't do it on the general case because the formatted ValueString may be interesting (e.g. for tabulate outputs)
            value = value.value
                
        if value is None:
            return self._nullval
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (datetime,time)):
            return self._stringify_datetime(value)
        elif isinstance(value, (float,Decimal)) and self._decimal_separator and self._decimal_separator != '.':
            return str(value).replace('.', self._decimal_separator)
        else:
            return super()._format_value(value, index, depth)
        

    # -------------------------------------------------------------------------
    # Internal helpers
    #    

    def _get_writer(self):
        if not self._writer:
            # NOTE: setting a value for escapechar (with doublequote=False) fails: value containing escapechar is not quoted (cf. test_table_json)
            self._writer = csv.writer(self.file, delimiter=self._delimiter, quotechar=self._quotechar)
        return self._writer
