from __future__ import annotations
from io import StringIO
import logging

from ..db import get_db_adapter_with_schema_and_table, DbAdapter
from .OutCsv import OutCsv

logger = logging.getLogger(__name__)


class OutDb(OutCsv):
    def __init__(self, out, table: str|tuple = None, **kwargs):        
        kwargs.pop('decimal_separator', None) # the memory CSV StringIO must use '.' as decimal separator in order to be understood by database 'COPY' command
        super().__init__(StringIO(), decimal_separator='.', **kwargs)

        if isinstance(out, DbAdapter):
            self.db = out
            out_schema = None
            out_table = None
            self._must_exit_db = False
        else:
            if isinstance(out, str):
                out = out.format(**kwargs)            
            self.db, out_schema, out_table = get_db_adapter_with_schema_and_table(out)
            self._must_exit_db = True

        if table:
            self.schema, self.table = self.db.split_name(table)
        else:
            if out_table:
                self.schema, self.table = (out_schema, out_table)
            else:
                raise ValueError(f"invalid db target: table name not provided")
        
        self.name = self.db.get_url(table=(self.schema, self.table), with_password=False)

    # -------------------------------------------------------------------------
    # OutFile subclassing
    #

    def _open_file(self):
        existing_headers = super()._open_file()

        # Create, drop or truncate table
        if not self._append:
            logger.debug(f"truncate table %s.%s", self.schema, self.table)
            self.db.truncate_table((self.schema, self.table))

        return existing_headers
                

    def _close_file(self):
        if not self.headers:
            if self.row_count == 0:
                return
            raise ValueError(f"cannot export rows to database: no headers")
                
        logger.debug(f"copy data to table %s.%s", self.schema, self.table)
        self.out.seek(0)
        self.db.load_from_csv(self.out, (self.schema, self.table), columns=self.headers, encoding=self._encoding, delimiter=self._delimiter, quotechar=self._quotechar, nullval=self._nullval)
        if self._must_exit_db:
            self.db.__exit__()


    # -------------------------------------------------------------------------
    # OutTable subclassing
    #
    
    def _get_existing_headers(self) -> list[str]|None:
        # Only export given headers, but check that they are in the target table
        column_names = self.db.get_table_column_names((self.schema, self.table))
        if not self.headers:
            raise ValueError(f'headers must be set')
        
        missing_columns = []
        for header in self.headers:
            if not header in column_names:
                missing_columns.append(header)

        if missing_columns:
            raise ValueError(f"column not found in out table: {', '.join(missing_columns)}")

        return []
