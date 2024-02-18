from __future__ import annotations

import csv
from io import IOBase
from pathlib import Path
from typing import Any

from ..text import skip_utf8_bom
from ..format import Format
from .. import files
from .utils import Row
from .InTable import InTable

class InCsv(InTable):
    def __init__(self, src: Path|str|IOBase, *, encoding: str = 'utf-8', delimiter: str = None, quotechar: str = None, nullval: str = None, **kwargs):     
        super().__init__(src, **kwargs)

        self._encoding = encoding
        self._delimiter, self._quotechar, self._nullval = Format.apply_csv_defaults(delimiter, quotechar, nullval)
        
        # in _prepare:
        self.file: IOBase = None
        self._must_close_file: bool = None


    def _prepare(self):
        if isinstance(self.src, IOBase):
            self.file = self.src
            self._must_close_file = False
        
        else:
            self.file = files.open(self.src, 'r', newline='', encoding=self._encoding)
            self._must_close_file = True

        if self._encoding == 'utf-8':
            if skip_utf8_bom(self.file):
                self._encoding = 'utf-8-sig'
        self._csv_reader = csv.reader(self.file, delimiter=self._delimiter, quotechar=self._quotechar)
        
        self.headers = []        
        try:
            for header in next(self._csv_reader):
                self.headers.append(str(header))
        except StopIteration:
            self.file.close()
            raise ValueError(f"no headers found in {self.name}")


    def _get_next_row(self):
        values = next(self._csv_reader)
        return Row(values, headers=self.headers, index=self.row_count)
    

    def _format(self, row: Row):
        for i, value in enumerate(row):
            if value == self._nullval:
                row[i] = None

        super()._format(row)
            

    def _end(self):
        if self.file and self._must_close_file:
            self.file.close()
