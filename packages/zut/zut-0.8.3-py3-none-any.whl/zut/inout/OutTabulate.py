from __future__ import annotations
import logging
from .OutTable import OutTable

try:
    from tabulate import tabulate
    _available = True
except ImportError:
    _available = False


logger = logging.getLogger(__name__)


class OutTabulate(OutTable):
    @classmethod
    def is_available(cls):
        return _available

    def __init__(self, out = None, **kwargs):
        super().__init__(out, **kwargs)
        self._start_atonce = False

    # -------------------------------------------------------------------------
    # OutTable subclassing
    #    
    def _export_delayed_rows(self):
        if not self._delayed_rows and not self.headers:
            print("no data", file=self.file)
            return
        
        rows = [self._prepare_row(row) for row in self._delayed_rows]
        if self.headers:
            result = tabulate(rows, headers=self.headers)
        else:
            result = tabulate(rows)
        
        print(result, file=self.file)


    def _get_existing_headers(self) -> list[str]|None:
        return []

    def _export_new_headers(self, headers: list[str]):
        pass
