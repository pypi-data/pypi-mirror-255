from __future__ import annotations

import logging
from hashlib import sha1
from pathlib import Path

from ..db import get_db_adapter_with_schema_and_table, DbAdapter
from ..colors import Colors
from ..text import skip_utf8_bom
from .InTable import InTable
from .utils import Row

logger = logging.getLogger(__name__)


class InDb(InTable):
    def __init__(self, src, query: str|Path = None, params: list|tuple|dict = None, offset: int = None, limit: int = None, **kwargs):
        if isinstance(src, DbAdapter):
            self.db = src
            schema = None
            table = None
            if self.db.tz and not 'tz' in kwargs:
                kwargs['tz'] = self.db.tz
            super().__init__(self.db.get_url(hide_password=True), **kwargs)
            self._must_exit_db = False
        else:
            self.db, schema, table = get_db_adapter_with_schema_and_table(src)
            super().__init__(self.db.get_url((schema, table)), **kwargs)
            self.name = self.db.get_url(table=(schema, table), hide_password=True)
            self._must_exit_db = True
        
        if isinstance(query, Path):
            with open(query, 'r', encoding='utf-8') as fp:
                skip_utf8_bom(fp)
                self._query = fp.read()
        else:
            self._query = query

        self._offset = offset
        self._limit = limit
        self._params = params
        if self._query:
            sha1_prefix = sha1(self._query.encode('utf-8')).hexdigest()[0:8]
            self.name = f"{self.name}#{sha1_prefix}"
        elif table:
            if self._params:
                raise ValueError(f'table query cannot contain params')
            self._query = self.db.get_select_table_query((schema, table))
        else:
            raise ValueError(f'neither a table or a query was given')

        if self._debug:
            logger.debug(f"execute {self.name} with params {self._params}, offset={self._offset}, limit={self._limit}\n{Colors.CYAN}{self._query}{Colors.RESET}")

        # set in __enter__() -> _prepare():
        self._cursor = None
        self._cursor_iterator = None


    def _prepare(self):
        self._cursor = self.db.cursor()
        self.db.execute_query(self._query, self._params, offset=self._offset, limit=self._limit, cursor=self._cursor)
        self._cursor_iterator = iter(self._cursor)

        self.headers = self.db.get_cursor_column_names(self._cursor)


    def _get_next_row(self):
        values = next(self._cursor_iterator)
        return Row(values, headers=self.headers, index=self.row_count)


    def _end(self):
        self._cursor.close()
        if self._must_exit_db:
            self.db.__exit__()
