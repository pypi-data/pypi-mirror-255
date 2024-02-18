from __future__ import annotations
from contextlib import nullcontext
from io import IOBase, StringIO, TextIOWrapper
import logging
import os
from pathlib import Path
import re
from typing import Any, Sequence, TypeVar, Generic
from urllib.parse import quote
from ..text import hide_url_password, skip_utf8_bom, build_url

try:
    from django.http import Http404 as NotFoundError
except ImportError:
    class NotFoundError(Exception):
        pass

class SeveralFoundError(Exception):
    pass

logger = logging.getLogger(__name__)

T_Connection = TypeVar('T_Connection')
T_Cursor = TypeVar('T_Cursor')
T_Composable = TypeVar('T_Composable')
T_Composed = TypeVar('T_Composed')


class DbAdapter(Generic[T_Connection, T_Cursor, T_Composable, T_Composed]):
    URL_SCHEME: str
    DEFAULT_SCHEMA = None
    ONLY_POSITIONAL_PARAMS = False
    EXPECTED_CONNECTION_TYPES: list[str]

    @classmethod
    def is_available(cls):
        raise NotImplementedError()
    

    def __init__(self, origin: T_Connection|str|dict, autocommit: bool = True):
        """
        Create a new adapter.
        - `origin`: an existing connection object, or the URL or django alias (e.g. 'default') for the new connection to create by the adapter.
        - `autocommit`: whether or not to auto-commit transactions (applies only for connections created by the adapter)
        """
        if not self.is_available():
            raise ValueError(f"cannot use {type(self).__name__} (not available)")
        
        if isinstance(origin, str):
            self._must_close_connection = True
            self._connection: T_Connection = None
            if ':' in origin or '/' in origin or ';' in origin or ' ' in origin:
                self._connection_url = origin
            else:
                from django.conf import settings
                if not origin in settings.DATABASES:
                    raise ValueError(f"key \"{origin}\" not found in django DATABASES settings")
                config: dict[str,Any] = settings.DATABASES[origin]
                
                build_url(
                    scheme = self.URL_SCHEME,
                    hostname = config.get('HOST', None),
                    port = config.get('PORT', None),
                    username = config.get('USER', None),
                    password = config.get('PASSWORD', None),
                    path = config.get('NAME', None),
                )

        elif isinstance(origin, dict):
            self._must_close_connection = True
            self._connection: T_Connection = None

            if 'NAME' in origin:
                # uppercase (as used by django)
                self._connection_url = build_url(
                    scheme = self.URL_SCHEME,
                    hostname = origin.get('HOST', None),
                    port = origin.get('PORT', None),
                    username = origin.get('USER', None),
                    password = origin.get('PASSWORD', None),
                    path = origin.get('NAME', None),
                )

            else:
                # lowercase (as used by some drivers' connection kwargs)
                self._connection_url = build_url(
                    scheme = self.URL_SCHEME,
                    hostname = origin.get('host', None),
                    port = origin.get('port', None),
                    username = origin.get('user', None),
                    password = origin.get('password', None),
                    path = origin.get('name', origin.get('dbname', None)),
                )

        else:
            origin = _get_connection_from_wrapper(origin)

            fulltype = type(origin).__module__ + '.' + type(origin).__qualname__
            if fulltype not in self.EXPECTED_CONNECTION_TYPES:
                raise ValueError(f"invalid connection type for {type(self).__name__}: {fulltype}")
            self._connection = origin
            self._connection_url: str = None
            self._must_close_connection = False
        
        self._autocommit: bool = autocommit


    def __enter__(self):
        return self


    def __exit__(self, exc_type = None, exc_val = None, exc_tb = None):
        if self._connection and self._must_close_connection:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"close %s (%s) connection to %s", type(self).__name__, type(self._connection).__module__ + '.' + type(self._connection).__qualname__, hide_url_password(self._connection_url))
            self._connection.close()


    @property
    def connection(self):
        if not self._connection:                
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"create %s connection to %s", type(self).__name__, hide_url_password(self._connection_url))
            self._connection = self._create_connection()
        return self._connection


    def cursor(self) -> T_Cursor:
        return self.connection.cursor()


    def _create_connection(self) -> T_Connection:
        raise NotImplementedError()


    def get_url(self, table: str|tuple = None, *, with_password = False):
        if self._connection_url:
            url = self._connection_url
        else:
            url = self._get_url_from_connection()

        if with_password:
            url = hide_url_password(url)

        if table:
            schema, table = self.split_name(table)
            if table:
                url += f"/"
                if schema:
                    url += quote(schema)
                    url += '.'
                url += quote(table)

        return url


    def _get_url_from_connection(self):
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    # Execution
    #    

    def _log_cursor_messages(self, cursor: T_Cursor):
        """
        Log cursor messages produced after execution of a query, if this cannot be done through a connection handler.
        """
        pass

    def execute_query(self, query: str, params: list|tuple|dict = None, *, cursor: T_Cursor = None, results: bool|TextIOWrapper|str|Path = False, offset: int = None, limit: int = None, query_id: str = None):
        """
        - `results`:
            - If True, return results as a dict list.
            - If False, ignore results.
            - If `warning`, produce a warning log if there is results.
            - If a stream or a str/path, write results as CSV to the given stream and return tuple (columns, rowcount)
        """
        from zut.inout import OutCsv
        try:
            from tabulate import tabulate
        except ImportError:
            tabulate = None

        if offset is not None or limit is not None:
            query = self.get_paginated_query(query, offset=offset, limit=limit)
                
        # Example of positional param: cursor.execute("INSERT INTO foo VALUES (%s)", ["bar"])
        # Example of named param: cursor.execute("INSERT INTO foo VALUES (%(foo)s)", {"foo": "bar"})
        if params is None:
            params = []
        elif isinstance(params, dict) and self.ONLY_POSITIONAL_PARAMS:
            query, params = self.to_positional_params(query, params)

        with nullcontext(cursor) if cursor else self.cursor() as _cursor:            
            # Execute query
            _cursor.execute(query, params)
            self._log_cursor_messages(_cursor)

            # Log number of affected rows for non-select queries
            if not _cursor.description and _cursor.rowcount >= 0:
                logger.debug("affected rows: %d", _cursor.rowcount)
                
            # Handle results
            if results == 'warning':
                if _cursor.description:
                    rows = [row for row in _cursor]                    
                    row_count = len(rows)
                    if row_count > 0:
                        columns = self.get_cursor_column_names(_cursor)

                        if tabulate:
                            text_rows = tabulate(rows[0:10], headers=columns)
                        else:
                            fp = StringIO()
                            with OutCsv(fp, headers=columns) as o:
                                for row in rows[0:10]:
                                    o.append(row)
                            text_rows = fp.getvalue()

                        if row_count > 10:
                            text_rows += "\n…"
                        logger.warning("query%s returned %d row%s:\n%s", f" {query_id}" if query_id else "", row_count, "s" if row_count > 1 else "", text_rows)
                return None
            
            elif isinstance(results, (IOBase,str,Path)):
                # Write results as CSV to the given stream
                columns = self.get_cursor_column_names(_cursor)
                
                with OutCsv(results, headers=columns, title=False) as o:
                    row_count = 0
                    for row in _cursor:
                        o.append(row)
                        row_count += 1
                    
                    results.seek(0)
                    return columns, row_count

            elif results:
                # Return results as a dict list
                columns = self.get_cursor_column_names(_cursor)
                return [{columns[i]: value for i, value in enumerate(row)} for row in _cursor]
            
            else:
                return None


    def execute_file(self, path: str|Path, params: list|tuple|dict = None, *, cursor: T_Cursor = None, results: bool|TextIOWrapper = False, offset: int = None, limit: int = None, encoding: str = 'utf-8') -> None:
        with open(path, 'r', encoding=encoding) as fp:
            skip_utf8_bom(fp)
            query = fp.read()
            
        self.execute_query(query, params, cursor=cursor, results=results, offset=offset, limit=limit)
    

    def execute_procedure(self, name: str|tuple, *args) -> T_Cursor:
        return NotImplementedError()


    # -------------------------------------------------------------------------
    # Particular types of results
    # 

    def get_scalar(self, query: str, params: list|tuple|dict = None, *, offset: int = None, limit: int = None):
        with self.cursor() as cursor:
            self.execute_query(query, params, cursor=cursor, offset=offset, limit=limit)

            iterator = iter(cursor)
            try:
                row = next(iterator)
            except StopIteration:
                raise NotFoundError()

            try:
                next(iterator)
                raise SeveralFoundError()
            except StopIteration:
                pass

            return row[0]
    

    def get_dict_single(self, query: str, params: list|tuple|dict = None):
        with self.cursor() as cursor:
            self.execute_query(query, params, cursor=cursor)

            iterator = iter(cursor)
            try:
                row = next(iterator)
            except StopIteration:
                raise NotFoundError()

            try:
                next(iterator)
                raise SeveralFoundError()
            except StopIteration:
                pass

            columns = self.get_cursor_column_names(cursor)
            return {columns[i]: value for i, value in enumerate(row)}
    

    def get_dict_list(self, query: str, params: list|tuple|dict = None):        
        with self.cursor() as cursor:
            self.execute_query(query, params, cursor=cursor)
            columns = self.get_cursor_column_names(cursor)
            return [{columns[i]: value for i, value in enumerate(row)} for row in cursor]
    

    def get_paginated_dict_list(self, query: str, params: list|dict = None, *, offset: int, limit: int):        
        paginated_query, total_query = self.get_paginated_and_total_query(query, offset=offset, limit=limit)

        rows = self.get_dict_list(paginated_query, params)
        total = self.get_scalar(total_query, params)
        return {"rows": rows, "total": total}


    # -------------------------------------------------------------------------
    # Queries
    #

    def to_positional_params(self, query: str, params: dict) -> tuple[str, Sequence[Any]]:
        from sqlparams import SQLParams  # not at the top because the enduser might not need this feature

        if not hasattr(self.__class__, '_params_formatter'):
            self.__class__._params_formatter = SQLParams('named', 'qmark')
        query, params = self.__class__._params_formatter.format(query, params)

        return query, params
    
    
    def get_paginated_query(self, query: str, *, offset: str, limit: int) -> str:
        paginated_query, _ = self.get_paginated_and_total_query(query, offset=offset, limit=limit)
        return paginated_query
    

    def get_paginated_and_total_query(self, query: str, *, offset: str, limit: int) -> tuple[str,str]:
        if offset is None:
            offset = 0
        elif isinstance(offset, str) and re.match(r"^[0-9]+$", offset):
            offset = int(offset)
        elif not isinstance(offset, int):
            raise TypeError(f"invalid type for offset: {type(limit).__name__} (expected int)")
        
        if isinstance(limit, str) and re.match(r"^[0-9]+$", limit):
            limit = int(limit)
        elif not isinstance(limit, int):
            raise TypeError(f"invalid type for limit: {type(limit).__name__} (expected int)")
        
        beforepart, selectpart, orderpart = self._parse_select_query(query)

        paginated_query = beforepart
        total_query = beforepart
        
        paginated_query += self._paginate_parsed_query(selectpart, orderpart, offset=offset, limit=limit)
        total_query += f"SELECT COUNT(*) FROM ({selectpart}) s"

        return paginated_query, total_query

    

    def _parse_select_query(self, query: str):
        import sqlparse  # not at the top because the enduser might not need this feature

        # Parse SQL to remove token before the SELECT keyword
        # example: WITH (CTE) tokens
        statements = sqlparse.parse(query)
        if len(statements) != 1:
            raise ValueError(f"query contains {len(statements)} statements")

        # Get first DML keyword
        dml_keyword = None
        dml_keyword_index = None
        order_by_index = None
        for i, token in enumerate(statements[0].tokens):
            if token.ttype == sqlparse.tokens.DML:
                if dml_keyword is None:
                    dml_keyword = str(token).upper()
                    dml_keyword_index = i
            elif token.ttype == sqlparse.tokens.Keyword:
                if order_by_index is None:
                    keyword = str(token).upper()
                    if keyword == "ORDER BY":
                        order_by_index = i

        # Check if the DML keyword is SELECT
        if not dml_keyword:
            raise ValueError(f"no SELECT found (query does not contain DML keyword)")
        if dml_keyword != 'SELECT':
            raise ValueError(f"first DML keyword is {dml_keyword}, expected SELECT")

        # Get part before SELECT (example: WITH)
        if dml_keyword_index > 0:
            tokens = statements[0].tokens[:dml_keyword_index]
            beforepart = ''.join(str(token) for token in tokens)
        else:
            beforepart = ''
    
        # Determine actual SELECT query
        if order_by_index is not None:
            tokens = statements[0].tokens[dml_keyword_index:order_by_index]
            selectpart = ''.join(str(token) for token in tokens)
            tokens = statements[0].tokens[order_by_index:]
            orderpart = ''.join(str(token) for token in tokens)
        else:
            tokens = statements[0].tokens[dml_keyword_index:]
            selectpart = ''.join(str(token) for token in tokens)
            orderpart = ''

        return beforepart, selectpart, orderpart
    

    def _paginate_parsed_query(self, selectpart: str, orderpart: str, *, offset: int, limit: int) -> str:
        return f"{selectpart} {orderpart} OFFSET {offset} LIMIT {limit}"
    

    def get_select_table_query(self, table: str|tuple, schema_only = False) -> T_Composed:
        """
        Build a query on the given table.

        If `schema_only` is given, no row will be returned (this is used to get information on the table).
        Otherwise, all rows will be returned.

        The return type of this function depends on the database engine.
        It is passed directly to the cursor's execute function for this engine.
        """
        raise NotImplementedError()


    def get_composable_param(self, value) -> T_Composable:
        if value is None:
            return "null"
        elif value == '__now__':
            return "CURRENT_DATETIME()"
        else:
            return self.escape_literal(value)
                

    def escape_identifier(self, value) -> T_Composable:
        raise NotImplementedError()
                

    def escape_literal(self, value) -> T_Composable:
        raise NotImplementedError()
    

    # -------------------------------------------------------------------------
    # Tables and columns
    #    

    @classmethod
    def split_name(cls, name: str|tuple) -> tuple[str,str]:
        if isinstance(name, tuple):
            return name
        
        try:
            pos = name.index('.')
            schema = name[0:pos]
            name = name[pos+1:]
        except ValueError:
            schema = cls.DEFAULT_SCHEMA
            name = name

        return (schema, name)
    

    def schema_exists(self, schema: str) -> bool:
        raise NotImplementedError()
    

    def create_schema(self, schema: str):
        raise NotImplementedError()
    

    def drop_schema(self, schema: str, cascade: bool = False):
        raise NotImplementedError()
    

    def table_exists(self, table: str|tuple) -> bool:
        raise NotImplementedError()


    def get_cursor_column_names(self, cursor: T_Cursor) -> list[str]:
        if not cursor.description:
            raise ValueError("No cursor description available")
        return [info[0] for info in cursor.description]
        

    def get_table_column_names(self, table: str|tuple) -> list[str]:
        query = self.get_select_table_query(table, schema_only=True)
        with self.cursor() as cursor:
            self.execute_query(query, cursor=cursor)
            return self.get_cursor_column_names(cursor)
    

    def drop_table(self, table: str|tuple):
        raise NotImplementedError()


    def truncate_table(self, table: str|tuple):
        raise NotImplementedError()


    def load_from_csv(self, file: os.PathLike|IOBase, table: str|tuple, columns: list[str] = None, encoding: str = 'utf-8', *, truncate: bool = False, noheaders: bool = False, delimiter: str = None, quotechar: str = None, nullval: str = None):
        raise NotImplementedError()
   

    # -------------------------------------------------------------------------
    # region Reinit (Django command)
    #    

    def move_all_to_new_schema(self, new_schema: str, old_schema: str = "public"):
        raise NotImplementedError()
    

    def drop_all(self, schema: str = "public"):
        raise NotImplementedError()
    
    # endregion


    def deploy_choices_table(self):
        raise NotImplementedError()


def _get_connection_from_wrapper(origin):    
    if type(origin).__module__.startswith(('django.db.backends.', 'django.utils.connection')):
        return origin.connection
    elif type(origin).__module__.startswith(('psycopg_pool.pool',)):
        return origin.connection()
    elif type(origin).__module__.startswith(('psycopg2.pool',)):
        return origin.getconn()
    else:
        return origin
