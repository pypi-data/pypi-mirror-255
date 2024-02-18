from __future__ import annotations
import logging
from pathlib import Path
from .InTable import InTable
from .OutExcel import OutExcel
from .utils import get_inout_name, split_excel_path

try:
    from ..excel import ExcelWorkbook
    _available = True
except ImportError:
    _available = False


logger = logging.getLogger(__name__)


class InExcel(InTable):
    @classmethod
    def is_available(cls):
        return _available


    def __init__(self, src, **kwargs):
        # Prepare arguments for base classes (InTable)
        if not isinstance(src, (str,Path)):
            raise ValueError(f"InExcel's src must be a str or path, got {type(src).__name__}: {src}")
        
        src, self.table_name = split_excel_path(src, default_table_name=OutExcel._DEFAULT_TABLE_NAME, **kwargs)
        
        # Initialize base classes (InTable)
        super().__init__(src=src, **kwargs)
        
        # Modify attributes set by base classes (InTable)
        self.name = get_inout_name(self.src) + f'#{self.table_name}'


    def _prepare(self):
        wb = ExcelWorkbook.get_or_create_cached(self.src)
        self.table = wb.get_table(self.table_name)
        self.headers = self.table.column_names if self.table.has_headers else None
        self._iterator = self.table.iterate(readonly=True)


    def _get_next_row(self):
        return next(self._iterator)
