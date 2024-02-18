from __future__ import annotations
from atexit import register as register_atexit
from datetime import date, datetime, time, timezone, tzinfo
from decimal import Decimal
from enum import Enum
from io import IOBase
import json
import logging
import os
from pathlib import Path
import sys
from types import FunctionType
from typing import Any, Iterable

from ..json import ExtendedJSONEncoder
from ..types import is_iterable_of
from .OutFile import OutFile

logger = logging.getLogger(__name__)


class OutTable(OutFile):
    """
    A mixin for appending and exporting tabular data.

    Must be subclassed (to implement read/write of value).
    """
    @classmethod
    def is_available(cls):
        return True
    
    def __init__(self, out: str|Path|IOBase|None = None, append: bool = False, headers: list[str] = None, tz: tzinfo = None, ms: bool = True, maxlen: int = None, dictkey: str|list[str] = None, **kwargs):
        if not self.is_available():
            raise ValueError(f"cannot use {type(self).__name__} (not available)")
    
        super().__init__(out, **kwargs)
        
        self._append = append

        self._start_atonce = True if headers else False # we consider than if headers are given now, they are final, so we don't need to wait for dict rows
        """ If true, delay rows until end of export """

        self._actually_started = False

        self.headers: list[str]|None = [str(header) for header in headers] if headers else None        
        self.row_count = 0

        self._delayed_rows: list[Iterable] = []

        self._reordering: list[int]|None = None
        self._reordering_default: list|None = None

        self._tz = timezone.utc if tz == 'utc' else tz
        """
        If given (as a tzinfo object or as 'local' or 'utc'), when aware datetimes and times are stringified or written to Excel, they will be expressed as naive in the given timezone.
        """

        self._ms = ms
        """
        If True, when datetimes and times are stringified or written to Excel, microseconds will be dropped.
        """

        self._maxlen = maxlen
        self._dictkeys = [dictkey] if isinstance(dictkey, str) else dictkey


    # -------------------------------------------------------------------------
    # Actions on start/end (see OutFile)
    #

    def __enter__(self) -> OutTable:
        if self._start_atonce:
            if self.headers:
                existing_headers = self._open_file()
                self._export_headers(existing_headers)
                self._actually_started = True

        if self.atexit:
            if callable(self.atexit):
                self.atexit(self)
            else:
                TableExitManager.append(self)

        return self
    

    def end(self):
        """
        This method is automatically executed when context ends (__exit__), except if `atexit` is truthy.
        """
        self._before_close_file()
        self._close_file()


    def _before_close_file(self):
        if not self._actually_started:        
            existing_headers = self._open_file()
            self._export_headers(existing_headers, at_end=True)
            self._actually_started = True

        self._export_delayed_rows()
        self._print_exported_count()

        self._delayed_rows = []


    def _print_exported_count(self):
        # symetrically to _print_title()

        if self._title is False:
            return
        if self.out == os.devnull:
            return
        
        if self.out in [sys.stdout, sys.stderr] and self.out.isatty():
            if self._title:
                print(f"\n{self.row_count} row{'s' if self.row_count > 1 else ''}", file=self.out)
        else:
            logger.info(f"{self.row_count} row{'s' if self.row_count > 1 else ''} {'appended' if self._append else 'exported'} to {self.name}")
    

    # -------------------------------------------------------------------------
    # Following methods are the core table export mechanism.
    # They are not supposed to be subclassed.
    #

    def _export_headers(self, existing_headers: list[str]|None, at_end=False):
        if not self.headers:
            if existing_headers:
                if not (at_end and not self._delayed_rows):
                    raise ValueError(f"cannot export table without headers: existing table contains headers ({', '.join(existing_headers)})")
            return
        
        if existing_headers is None:
            if self.headers:
                if not (at_end and not self._delayed_rows):
                    raise ValueError(f"cannot export table with headers: existing table cannot contain headers")
            return
        
        if existing_headers == self.headers:
            return

        if len(existing_headers) == 0:
            self._export_new_headers(self.headers)
            return

        # From now own, we must compare existing and target headers
        self._reordering = []
        self._reordering_default = [None] * len(existing_headers)

        for header in self.headers:
            try:
                index = existing_headers.index(header)
                self._reordering.append(index)
            except ValueError:
                self._reordering_default.append(None)
                index = len(self._reordering_default) - 1
                self._reordering.append(index)
                self._add_new_header(header, index)
    

    def append(self, row):
        if isinstance(row, dict):
            row = self._dict_to_row(row)        
        else:
            row = self._iterable_to_row(row)

        if self._start_atonce:
            self._export_row(row)
        else:
            self._delayed_rows.append(row)
        
        self.row_count += 1


    def _export_row(self, row: Iterable):
        if not self._actually_started:
            existing_headers = self._open_file()
            self._export_headers(existing_headers)
            self._actually_started = True

        self._export_prepared_row(self._prepare_row(row))


    def _prepare_row(self, data: Iterable):
        if not self._reordering:
            row = [self._format_value(value, i) for i, value in enumerate(data)]
            if self.headers:
                while len(row) < len(self.headers):
                    row.append(self._format_value(None, len(row)-1))
            return row
        
        else:
            row = list(self._reordering_default)
            for i, value in enumerate(data):
                value = self._format_value(value, i)
                if i < len(self._reordering):
                    index = self._reordering[i]
                    row[index] = value
                else:
                    row.append(value)

            return row


    def _iterable_to_row(self, data: Iterable):
        if self.headers is not None and len(data) != len(self.headers):
            logger.warning(f"row {self.row_count+1} length: {len(data)} (expected headers length: {len(self.headers)})")
        
        return data
        

    def _dict_to_row(self, data: dict):
        row = [None] * (len(self.headers) if self.headers else 0)

        for header, value in data.items():
            index = self._fetch_header(header)
            while index >= len(row):
                row.append(None)
            row[index] = value
            
        return row


    def _fetch_header(self, header: str) -> int:
        if not isinstance(header, str):
            header = str(header)

        if self.headers is None:
            self.headers = []

        try:
            index = self.headers.index(header)
        except:
            self.headers.append(header)
            index = len(self.headers) - 1

            if self._actually_started:
                logger.warning(f"row {self.row_count + 1} header \"{header}\" not found in exported headers: values will be appended at column {len(self.headers)} with an empty header")
            
        return index


    # -------------------------------------------------------------------------
    # These methods are available for subclassing. 
    #
    def _open_file(self) -> list[str]|None:
        """
        For OutTable and its subclass, `_open_table()` must return existing headers.

        Depending on the situation, `_get_existing_headers()` may be called before opening the underlying file (in order to avoid potential file locking)
        or after opening the underlying file (for example the Excel workbook for OutExcel).
        """
        existing_headers = self._get_existing_headers()
        super()._open_file()
        return existing_headers
    

    def _get_existing_headers(self) -> list[str]|None:
        """
        Get headers to consider in the existing target.

        Return a list (including empty list) if headers make sense.
        Return `None` if headers cannot be used at all.
        """
        raise NotImplementedError(f"method must be implemented by {type(self).__name__}")


    def _export_new_headers(self, headers: list[str]):
        """
        Export headers when the list of exiting headers is empty.
        """        
        for index, header in enumerate(headers):
            self._add_new_header(header, index)


    def _add_new_header(self, header: str, index: int):
        """
        Add a new header to an existing list of headers.
        """
        raise NotImplementedError(f"method must be implemented by {type(self).__name__}")


    def _export_prepared_row(self, row: Iterable):
        """
        Export a row that has been reordered (if necessary) to match existing headers + newly added headers.
        """
        raise NotImplementedError(f"method must be implemented by {type(self).__name__}")


    def _format_value(self, value: Any, index: int, depth: int = 0) -> Any:
        if value is None:
            return None
        
        elif isinstance(value, str):            
            if self._maxlen is not None and len(value) > self._maxlen:
                value = value[0:self._maxlen-1] + '…'
            return value
        
        elif isinstance(value, Enum):
            return value.name
        
        elif isinstance(value, (list,tuple)):
            # Try to display as a list of elements separated by "|"
            if depth == 0 and is_iterable_of(value, (str,int,float,Decimal,bool,type(None),date,datetime,time,dict)):
                parts = []
                for element in value:
                    if element is None:
                        part = ''
                    else:                      
                        part = self._format_value(element, index, depth + 1)
                        
                        if part is not None and not isinstance(part, str):
                            part = str(part)

                        if part is None or '|' in part:
                            # cancel
                            parts = None
                            break
                    parts.append(part)

                if parts is not None:
                    return '|'.join(parts)
            
            return json.dumps(value, cls=ExtendedJSONEncoder)
        
        elif isinstance(value, dict):
            if self._dictkeys:
                representation = self._get_dict_representation(value)
                if representation:
                    return representation
            return json.dumps(value, cls=ExtendedJSONEncoder)
        
        else:
            # NOTE: we don't transform everything in strings, because the underlying output system may take into account the actual type
            # (example: tabulate will align numeric values differently)
            return value
        
    
    def _get_dict_representation(self, data: dict):
        for key in self._dictkeys:
            if key in data:
                return data[key]


    def _export_delayed_rows(self):
        for row in self._delayed_rows:
            self._export_row(row)


    # -------------------------------------------------------------------------
    # Utils
    #
    def _stringify_datetime(self, value: datetime|time):
        # NOTE: the result is compatible with Excel if self._tz is given.

        if value.tzinfo:
            if self._tz:
                value = value.astimezone(None if self._tz == 'local' else self._tz)
                use_tzinfo = False
            else:
                use_tzinfo = True
        else:
            use_tzinfo = False

        # Format microseconds
        if value.microsecond == 0 or not self._ms:
            mspart = ''
        else:
            mspart = '.' + value.strftime('%f')
        
        # Format tzinfo and microseconds
        if use_tzinfo:
            tzpart = value.strftime('%z')
            if len(tzpart) == 5:
                tzpart = tzpart[0:3] + ':' + tzpart[3:]
        else:
            tzpart = ''

        return value.strftime("%H:%M:%S" if isinstance(value, time) else "%Y-%m-%d %H:%M:%S") + mspart + tzpart



class TableExitManager:
    instance: TableExitManager = None

    @classmethod
    def append(cls, table: OutTable):
        if not cls.instance:
            cls.instance = TableExitManager()
            register_atexit(cls.instance.end)
        cls.instance.tables.append(table)


    def __init__(self):
        self.tables: list[OutTable] = []


    def end(self):            
        from .OutExcel import OutExcel
        from ..excel import ExcelWorkbook

        for table in self.tables:
            table._before_close_file()


        has_outexcel = False

        for table in self.tables:
            if isinstance(table, OutExcel):
                has_outexcel = True
            else:
                table._close_file()

        if has_outexcel:
            ExcelWorkbook.close_all_cached()
