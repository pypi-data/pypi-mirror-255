from __future__ import annotations
from datetime import datetime, time
import logging
from pathlib import Path
from typing import Any, Callable, Iterable

from zut.datetime import make_naive
from .. import files
from .OutTable import OutTable
from .utils import get_inout_name, split_excel_path

try:
    from ..excel import ExcelWorkbook
    _available = True
except ImportError:
    _available = False


logger = logging.getLogger(__name__)


class OutExcel(OutTable):
    file: ExcelWorkbook
    _DEFAULT_TABLE_NAME = 'Out'

    @classmethod
    def is_available(cls):
        return _available
    

    def __init__(self, out = None, atexit: bool|Callable = True, **kwargs):
        # Prepare arguments for base classes (OutTable, OutFile)
        if not isinstance(out, (str,Path)):
            raise ValueError(f"OutExcel's out must be a str or path, got {type(out).__name__}: {out}")
        
        out, self.table_name = split_excel_path(out, default_table_name=OutExcel._DEFAULT_TABLE_NAME, **kwargs)
        
        # Initialize base classes (OutTable, OutFile)
        super().__init__(out=out, atexit=atexit, **kwargs)
        
        # Modify attributes set by base classes (OutTable, OutFile)
        self.name = get_inout_name(self.out) + f'#{self.table_name}'


    # -------------------------------------------------------------------------
    # OutFile subclassing
    #

    def _open_file(self):
        self._print_title()

        parent = files.dirname(self.out)
        if parent and not files.exists(parent):
            files.makedirs(parent)

        self.file = ExcelWorkbook.get_or_create_cached(self.out)
        self._must_close_file = True

        self.table = self.file.get_table(self.table_name, default=None)
        if not self.table:
            self.table = self.file.create_table(self.table_name, no_headers=True if not self.headers else False)
        
        if not self._append:
            self.table.truncate()

        existing_headers = self._get_existing_headers()
        return existing_headers


    # -------------------------------------------------------------------------
    # OutTable subclassing
    #

    def _get_existing_headers(self) -> list[str]|None:
        return self.table.column_names if self.table.has_headers else None
    

    def _add_new_header(self, header: str, index: int):
        self.table.insert_col(header)
    

    def _export_prepared_row(self, row: Iterable):
        table_row = self.table.insert_row()
        
        for i, value in enumerate(row):
            if value is None:
                # keep default formula if any (applied during table.erase_cell(), called from table.insert_row())
                continue
            
            if i < len(table_row):            
                table_row[i] = value
            else:
                logger.warning(f'ignore values from index {i} ({value})')
                break


    def _format_value(self, value: Any, index: int, depth: int = 0) -> Any:
        if isinstance(value, (datetime,time)) and value.tzinfo:
            if value.tzinfo:
                # Excel does not support timezones in datetimes
                if not self._tz:
                    if not hasattr(self, '_warned_tz'):
                        logger.warning(f'stripped timezone info from datetimes and times (first for: {value}) as Excel date type is not compatible with timezones - consider specifying `tz` argument to indicate which timezone to use for your Excel table')
                        self._warned_tz = True
                value = make_naive(value, self._tz)

            if value.microsecond and not self._ms:
                value = value.replace(microsecond=0)

            return value
        else:
            return super()._format_value(value, index, depth)
