from __future__ import annotations
from contextlib import nullcontext
from io import IOBase
import logging
import os
from pathlib import Path
import re
from urllib.parse import urlparse

from ..text import build_url, skip_utf8_bom
from ..format import Format
from ..choices import _registered_choices_tables
from .base import DbAdapter, T_Connection, T_Cursor, T_Composable, T_Composed

logger = logging.getLogger(__name__)

# psycopg v3
try:
    from psycopg import Connection as v3_Connection, Cursor as v3_Cursor, sql as v3_sql, connect as v3_connect
    from psycopg.errors import Diagnostic
    v3_Composable = v3_sql.Composable
    v3_Composed = v3_sql.Composed
except ImportError:
    v3_Connection = type(None)
    v3_Cursor = type(None)
    v3_Composable = type(None)
    v3_Composed = type(None)
    v3_sql = None

# psycopg v2
try:
    from psycopg2 import sql as v2_sql, connect as v2_connect
    from psycopg2.extensions import connection as v2_Connection, cursor as v2_Cursor
    v2_Composable = v2_sql.Composable
    v2_Composed = v2_sql.Composed
except:
    v2_Connection = type(None)
    v2_Cursor = type(None)
    v2_Composable = type(None)
    v2_Composed = type(None)
    v2_sql = None


class PgBaseAdapter(DbAdapter[T_Connection, T_Cursor, T_Composable, T_Composed]):
    URL_SCHEME = 'postgresql' # See: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
    DEFAULT_SCHEMA = 'public'
    _sql = v3_sql
    

    @classmethod
    def is_available(cls):
        return cls._sql is not None
   

    # -------------------------------------------------------------------------
    # Execute utils
    #
    
    def execute_procedure(self, name: str|tuple, *args) -> T_Cursor:
        schema, name = self.split_name(name)
        
        query = "CALL "
        params = []
            
        if schema:    
            query +="{}."
            params += [self.escape_identifier(schema)]

        query += "{}"
        params += [self.escape_identifier(name)]

        query += "(" + ", ".join(['{}'] * len(args)) + ")"
        params += [self.get_composable_param(arg) for arg in args]

        with self.cursor() as cursor:
            with self.register_notice_handler(if_exists=None, logprefix=f"pg:{schema + '.' if schema and schema != self.DEFAULT_SCHEMA else ''}{name}"):
                cursor.execute(self._sql.SQL(query).format(*params))
                return cursor
            

    def register_notice_handler(self, if_exists = '__raise__', logprefix = 'pg'):
        """
        Usage example with Django:

        ```
        from django.apps import AppConfig
        from django.db.backends.signals import connection_created
        from zut import PgAdapter # or 'Pg2Adapter' for psycopg2

        class MyDjangoProjectConfig(AppConfig):
            default_auto_field = 'django.db.models.BigAutoField'
            name = 'mydjangiproject'
            
            def ready(self):
                connection_created.connect(connection_created_receiver)

        def connection_created_receiver(sender, connection, **kwargs):
            if connection.alias == "default":
                Pg2Adapter(connection).register_notice_handler()
        ```
        """
        raise NotImplementedError() # implemented in concrete subclasses


    # -------------------------------------------------------------------------
    # Queries
    #
    
    def get_select_table_query(self, table: str|tuple, schema_only = False) -> PgAdapter._sql.Composed:
        schema, table = self.split_name(table)

        query = "SELECT * FROM "
        params = []
            
        if schema:    
            query +="{}."
            params += [self.escape_identifier(schema)]

        query += "{}"
        params += [self.escape_identifier(table)]
        
        if schema_only:
            query += ' WHERE false'

        return self._sql.SQL(query).format(*params)


    def get_composable_param(self, value):
        if value is None:
            return self._sql.SQL("null")
        elif value == '__now__':
            return self._sql.SQL("NOW()")
        elif isinstance(value, self._sql.Composable):
            return value
        else:
            return self.escape_literal(value)
        

    def escape_identifier(self, value) -> PgAdapter._sql.Composable:
        return self._sql.Identifier(value)
    

    def escape_literal(self, value) -> PgAdapter._sql.Composable:
        return self._sql.Literal(value)
    

    # -------------------------------------------------------------------------
    # region Schemas, tables and columns
    #    

    def schema_exists(self, schema: str) -> bool:
        query = "SELECT EXISTS (SELECT FROM pg_namespace WHERE nspname = %s)"
        params = [schema]

        return self.get_scalar(query, params)
    

    def create_schema(self, schema: str):
        query = "CREATE SCHEMA {}"
        params = [self._sql.Identifier(schema)]

        return self.execute_query(self._sql.SQL(query).format(*params))
    

    def drop_schema(self, schema: str, cascade: bool = False):
        query = "DROP SCHEMA {}"
        params = [self._sql.Identifier(schema)]

        if cascade:
            query += " CASCADE"

        return self.execute_query(self._sql.SQL(query).format(*params))
    

    def table_exists(self, table: str|tuple) -> bool:
        schema, table = self.split_name(table)

        query = "SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = %s AND tablename = %s)"
        params = [schema, table]

        return self.get_scalar(query, params)
    

    def drop_table(self, table: str|tuple):
        schema, table = self.split_name(table)
        
        query = "DROP TABLE "
        params = []
            
        if schema:    
            query +="{}."
            params += [self.escape_identifier(schema)]

        query += "{}"
        params += [self.escape_identifier(table)]

        self.execute_query(self._sql.SQL(query).format(*params))
        

    def truncate_table(self, table: str|tuple):
        schema, table = self.split_name(table)
        
        query = "TRUNCATE "
        params = []
            
        if schema:    
            query +="{}."
            params += [self.escape_identifier(schema)]

        query += "{}"
        params += [self.escape_identifier(table)]

        self.execute_query(self._sql.SQL(query).format(*params))

    # endregion
            

    def load_from_csv(self, file: os.PathLike|IOBase, table: str|tuple, columns: list[str] = None, encoding: str = 'utf-8', *, truncate: bool = False, noheaders: bool = False, delimiter: str = None, quotechar: str = None, nullval: str = None):
        sche, tab = self.split_name(table)
        
        delimiter, quotechar, nullval = Format.apply_csv_defaults(delimiter, quotechar, nullval)

        if truncate:                
            self.truncate_table((sche, tab))
        
        query = "COPY "
        params = []
            
        if sche:    
            query +="{}."
            params += [self.escape_identifier(sche)]

        query += "{}"
        params += [self.escape_identifier(tab)]

        if columns:
            query += " ("
            for i, column in enumerate(columns):
                if i > 0:
                    query += ", "
                query += "{}"

                params.append(self.escape_identifier(column))
            query += ")"

        query += " FROM STDIN (FORMAT csv"

        query += ', ENCODING {}'
        params.append('utf-8' if encoding == 'utf-8-sig' else self.escape_literal(encoding))

        query += ', DELIMITER {}'
        params.append(self.escape_literal(delimiter))

        query += ', QUOTE {}'
        params.append(self.escape_literal(quotechar))
        
        query += ', ESCAPE {}'
        params.append(self.escape_literal(quotechar))

        query += ', NULL {}'
        params.append(self.escape_literal(nullval))

        if not noheaders:
            query += ", HEADER match"

        query += ")"

        with nullcontext(file) if isinstance(file, IOBase) else open(file, "rb") as fp:
            skip_utf8_bom(fp)
            self._actual_copy(self._sql.SQL(query).format(*params), fp)
   

    # -------------------------------------------------------------------------
    # region Reinit (Django command)
    #    

    def move_all_to_new_schema(self, new_schema: str, old_schema: str = "public"):
        query = """DO LANGUAGE plpgsql $$
    DECLARE
        old_schema name = {old_schema};
        new_schema name = {new_schema};
        sql_query text;
    BEGIN
        -- Create schema
        sql_query = format('CREATE SCHEMA %I', new_schema);
        RAISE NOTICE 'applying %', sql_query;
        EXECUTE sql_query;
    
        -- Move tables and views
        FOR sql_query IN
            SELECT
                format('ALTER %s %I.%I SET SCHEMA %I', CASE WHEN table_type IN ('BASE TABLE') THEN 'TABLE' ELSE table_type END, table_schema, table_name, new_schema)
            FROM information_schema.tables
            WHERE table_schema = old_schema
            AND table_name NOT IN ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
        LOOP
            RAISE NOTICE 'applying %', sql_query;
            EXECUTE sql_query;
        END LOOP;
    
        -- Move routines
        FOR sql_query IN
            SELECT
                format('ALTER %s %I.%I%s SET SCHEMA %I', routine_type, routine_schema, routine_name, routine_params, new_schema)
            FROM (
                SELECT
                    specific_name, routine_type, routine_schema, routine_name
                    ,CASE WHEN routine_params IS NULL THEN '()' ELSE CONCAT('(',  routine_params, ')') END AS routine_params
                FROM (
                    SELECT
                        r.specific_name
                        ,r.routine_type, r.routine_schema, r.routine_name
                        ,string_agg(p.data_type, ', ' order by p.ordinal_position ) AS routine_params
                    FROM information_schema.routines r
                    LEFT OUTER JOIN information_schema.parameters p ON p.specific_name = r.specific_name
                    GROUP BY
                        r.specific_name
                        ,r.routine_type, r.routine_schema, r.routine_name
                ) s
            ) s
            WHERE routine_schema = old_schema
            -- postgis:
            AND routine_name NOT LIKE 'box%%'
            AND routine_name NOT LIKE '%%geography%%' AND routine_name NOT LIKE 'geog_%%'
            AND routine_name NOT LIKE '%%geometry%%' AND routine_name NOT LIKE 'geom%%'
            AND routine_name NOT LIKE 'gidx_%%'
            AND routine_name NOT LIKE 'gserialized_%%'
            AND routine_name NOT LIKE 'overlaps_%%'
            AND routine_name NOT LIKE 'postgis_%%' AND routine_name NOT LIKE '_postgis_%%' AND routine_name NOT LIKE 'pgis_%%'
            AND routine_name NOT LIKE 'spheroid_%%'
            AND routine_name NOT LIKE 'st_%%' AND routine_name NOT LIKE '_st_%%'
            AND routine_name NOT IN ('addauth', 'bytea', 'checkauth', 'checkauthtrigger', 'contains_2d', 'disablelongtransactions', 'enablelongtransactions', 'equals', 'find_srid', 'get_proj4_from_srid', 'gettransactionid', 'is_contained_2d', 'json', 'jsonb', 'lockrow', 'longtransactionsenabled', 'path', 'point', 'polygon', 'text', 'unlockrows')
            -- unaccent:
            AND routine_name NOT LIKE 'unaccent%%'
        LOOP
            RAISE NOTICE 'applying %', sql_query;
            EXECUTE sql_query;
        END LOOP;
    END; $$
    """
        params = {
            'old_schema': self.escape_literal(old_schema),
            'new_schema': self.escape_literal(new_schema if new_schema else "public"),
        }

        with self.cursor() as cursor:
            with self.register_notice_handler(if_exists=None, logprefix=f"pg:move_all_to_new_schema"):
                cursor.execute(self._sql.SQL(query).format(**params))


    def drop_all(self, schema: str = "public"):
        query = """DO LANGUAGE plpgsql $$
    DECLARE
        old_schema name = {old_schema};
        sql_query text;
    BEGIN
        -- Remove foreign-key constraints
        FOR sql_query IN
            SELECT
                format('ALTER TABLE %I.%I DROP CONSTRAINT %I', table_schema, table_name, constraint_name)
            FROM information_schema.table_constraints
            WHERE table_schema = old_schema AND constraint_type = 'FOREIGN KEY'
            AND table_name NOT IN ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
        LOOP
            RAISE NOTICE 'applying %', sql_query;
            EXECUTE sql_query;
        END LOOP;

        -- Drop tables and views
        FOR sql_query IN
            SELECT
                format('DROP %s IF EXISTS %I.%I CASCADE', CASE WHEN table_type IN ('BASE TABLE') THEN 'TABLE' ELSE table_type END, table_schema, table_name)
            FROM information_schema.tables
            WHERE table_schema = old_schema
            AND table_name NOT IN ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
        LOOP
            RAISE NOTICE 'applying %', sql_query;
            EXECUTE sql_query;
        END LOOP;
    
        -- Drop routines
        FOR sql_query IN
            SELECT
                format('DROP %s IF EXISTS %I.%I%s CASCADE', routine_type, routine_schema, routine_name, routine_params)
            FROM (
                SELECT
                    specific_name, routine_type, routine_schema, routine_name
                    ,CASE WHEN routine_params IS NULL THEN '()' ELSE CONCAT('(',  routine_params, ')') END AS routine_params
                FROM (
                    SELECT
                        r.specific_name
                        ,r.routine_type, r.routine_schema, r.routine_name
                        ,string_agg(p.data_type, ', ' order by p.ordinal_position ) AS routine_params
                    FROM information_schema.routines r
                    LEFT OUTER JOIN information_schema.parameters p ON p.specific_name = r.specific_name
                    GROUP BY
                        r.specific_name
                        ,r.routine_type, r.routine_schema, r.routine_name
                ) s
            ) s
            WHERE routine_schema = old_schema
            -- postgis:
            AND routine_name NOT LIKE 'box%%'
            AND routine_name NOT LIKE '%%geography%%' AND routine_name NOT LIKE 'geog_%%'
            AND routine_name NOT LIKE '%%geometry%%' AND routine_name NOT LIKE 'geom%%'
            AND routine_name NOT LIKE 'gidx_%%'
            AND routine_name NOT LIKE 'gserialized_%%'
            AND routine_name NOT LIKE 'overlaps_%%'
            AND routine_name NOT LIKE 'postgis_%%' AND routine_name NOT LIKE '_postgis_%%' AND routine_name NOT LIKE 'pgis_%%'
            AND routine_name NOT LIKE 'spheroid_%%'
            AND routine_name NOT LIKE 'st_%%' AND routine_name NOT LIKE '_st_%%'
            AND routine_name NOT IN ('addauth', 'bytea', 'checkauth', 'checkauthtrigger', 'contains_2d', 'disablelongtransactions', 'enablelongtransactions', 'equals', 'find_srid', 'get_proj4_from_srid', 'gettransactionid', 'is_contained_2d', 'json', 'jsonb', 'lockrow', 'longtransactionsenabled', 'path', 'point', 'polygon', 'text', 'unlockrows')
            -- unaccent:
            AND routine_name NOT LIKE 'unaccent%%'
        LOOP
            RAISE NOTICE 'applying %', sql_query;
            EXECUTE sql_query;
        END LOOP;
    END; $$
    """
        params = {
            'old_schema': self.escape_literal(schema)
        }

        with self.cursor() as cursor:
            with self.register_notice_handler(if_exists=None, logprefix=f"pg:drop_all"):
                cursor.execute(self._sql.SQL(query).format(**params))
    

    # endregion

    def deploy_choices_table(self):
        with self.cursor() as cursor:
            for app_label, cls_list in _registered_choices_tables.items():
                for cls in cls_list:
                    db_table = cls.__name__.lower()
                    if app_label:
                        db_table = f'{app_label}_{db_table}'

                    logger.debug("deploy choices table %s", db_table)

                    # Create table if not exists
                    max_value_typebase = 1
                    for member in cls:
                        if issubclass(cls, int):
                            value_typebase = member.value
                        else:
                            value_typebase = len(member.value)
                        if value_typebase > max_value_typebase:
                            max_value_typebase = value_typebase

                    if issubclass(cls, int):
                        choices_value_type = 'smallint' if max_value_typebase <= 32767 else 'bigint'
                    else:
                        choices_value_type = f'char({max_value_typebase})'

                    query = "CREATE TABLE IF NOT EXISTS {choices_table} ("
                    query += "\n    id {choices_value_type} NOT NULL PRIMARY KEY"
                    query += "\n    ,name text NOT NULL UNIQUE"
                    query += "\n    ,label text NOT NULL UNIQUE"
                    query += "\n    ,created timestamptz NOT NULL DEFAULT now()"
                    query += "\n    ,updated timestamptz NOT NULL DEFAULT now()"
                    query += ");"

                    cursor.execute(self._sql.SQL(query).format(
                        choices_table = self.escape_identifier(db_table),
                        choices_value_type = self._sql.SQL(choices_value_type),
                    ))

                    # Upsert members
                    query = "INSERT INTO {} AS d (id, name, label, created, updated)"
                    params = [self.escape_identifier(db_table)]
                    query += "\nVALUES"
                    for i, member in enumerate(cls):
                        query += "\n    %s({}, {}, {}, now(), now())" % (',' if i > 0 else '')
                        params += [self.escape_literal(member.value), self.escape_literal(member.name), self.escape_literal(member.label)]
                    query += "\nON CONFLICT (id) DO UPDATE SET"
                    query += "\n    name = excluded.name"
                    query += "\n    ,label = excluded.label"
                    query += "\n    ,updated = CASE WHEN d.name != excluded.name OR d.label != excluded.label THEN now() ELSE d.updated END"
                    query += "\n;"

                    cursor.execute(self._sql.SQL(query).format(*params))


class PgAdapter(PgBaseAdapter[v3_Connection, v3_Cursor, v3_Composable, v3_Composed]):
    EXPECTED_CONNECTION_TYPES = ['psycopg.Connection']
    _sql = v3_sql

    def _create_connection(self) -> T_Connection:
        conn = v3_connect(self._connection_url, autocommit=self._autocommit)
        return conn
    
    
    def _get_url_from_connection(self):
        with self.cursor() as cursor:
            cursor.execute("SELECT session_user, inet_server_addr(), inet_server_port(), current_database()")
            user, host, port, dbname = next(iter(cursor))
        return build_url(scheme=self.URL_SCHEME, username=user, hostname=host, port=port, path='/'+dbname)


    def _actual_copy(self, query, fp):
        BUFFER_SIZE = 65536

        with self.cursor() as cursor:
            with cursor.copy(query) as copy:
                while True:
                    data = fp.read(BUFFER_SIZE)
                    if not data:
                        break
                    copy.write(data)


    def register_notice_handler(self, logprefix = None, if_exists = '__raise__'):
        if self.connection._notice_handlers:
            if if_exists != '__raise__':
                return nullcontext(if_exists)
            raise ValueError(f"notice handler already registered: {self.connection._notice_handlers}")

        return PgNoticeManager(self.connection, logprefix)


class Pg2Adapter(PgBaseAdapter[v2_Connection, v2_Cursor, v2_Composable, v3_Composed]):
    EXPECTED_CONNECTION_TYPES = ['psycopg2.extensions.connection']
    _sql = v2_sql

    def _create_connection(self) -> T_Connection:
        kwargs = {}
        
        r = urlparse(self._connection_url)

        if r.hostname:
            kwargs['host'] = r.hostname
        if r.port:
            kwargs['port'] = r.port

        name = r.path.lstrip('/')
        if name:
            kwargs['dbname'] = name

        if r.username:
            kwargs['user'] = r.username
        if r.password:
            kwargs['password'] = r.password

        conn = v2_connect(**kwargs)
        conn.autocommit = self._autocommit
        return conn
    

    def _get_url_from_connection(self):    
        params = self.connection.get_dsn_parameters()
        return build_url(
            scheme=self.URL_SCHEME,
            path='/' + params.get('dbname', None),
            hostname=params.get('host', None),
            port=params.get('port', None),
            username=params.get('user', None),
            password=params.get('password', None),
        )
    

    def _actual_copy(self, query, fp):
        with self.cursor() as cursor:
            cursor.copy_expert(query, fp)
    

    def register_notice_handler(self, logprefix = None, if_exists = '__raise__'):
        if self.connection.notices:
            if if_exists != '__raise__':
                return nullcontext(if_exists)
            raise ValueError(f"notice handler already registered: {self.connection.notices}")

        return Pg2NoticeHandler(self.connection, logprefix)


class PgNoticeManager:
    """
    This class can be used as a context manager that remove the handler on exit.

    The actual handler required by psycopg 3 `connection.add_notice_handler()` is the `pg_notice_handler` method.
    """
    def __init__(self, connection, logprefix: str = None):
        self.connection = connection
        self.logger = logging.getLogger(logprefix) if logprefix else None
        self.connection.add_notice_handler(self.handler)

    def __enter__(self):
        return self.handler
    
    def __exit__(self, *args):
        self.connection._notice_handlers.remove(self.handler)


    def handler(self, diag: Diagnostic):
        return pg_notice_handler(diag, logger=self.logger)


def pg_notice_handler(diag: Diagnostic, logger: logging.Logger = None):
    """
    Handler required by psycopg 3 `connection.add_notice_handler()`.
    """
    # determine level
    level = pg_get_logging_level(diag.severity_nonlocalized)
    
    # determine logger
    if logger:
        logger = logger
        message = diag.message_primary
    else:
        # parse context
        m = re.match(r"^fonction [^\s]+ (\w+)", diag.context or '')
        if m:
            logger = logging.getLogger(f"pg:{m[1]}")
            message = diag.message_primary
        else:
            logger = logging.getLogger("pg")
            message = f"{diag.context or ''}{diag.message_primary}"

    # write log
    logger.log(level, message)


class Pg2NoticeHandler:
    """
    This class is the actual handler required by psycopg 2 `connection.notices`.
    
    It can also be used as a context manager that remove the handler on exit.
    """
    _pg_msg_re = re.compile(r"^(?P<pglevel>[A-Z]+)\:\s(?P<message>.+(?:\r?\n.*)*)$", re.MULTILINE)

    def __init__(self, connection, logprefix: str = None):
        self.connection = connection
        self.logger = logging.getLogger(logprefix if logprefix else 'pg')
        self.connection.notices = self

    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.connection.notices = []

        
    def append(self, fullmsg: str):
        fullmsg = fullmsg.strip()
        m = self._pg_msg_re.match(fullmsg)
        if not m:
            self.logger.error(fullmsg)
            return

        message = m.group("message").strip()
        severity = m.group("pglevel")
        level = pg_get_logging_level(severity)

        self.logger.log(level, message)


def pg_get_logging_level(severity_nonlocalized: str):
    if severity_nonlocalized.startswith('DEBUG'): # not sent to client (by default)
        return logging.DEBUG
    elif severity_nonlocalized == 'LOG': # not sent to client (by default), written on server log (LOG > ERROR for log_min_messages)
        return logging.DEBUG
    elif severity_nonlocalized == 'NOTICE': # sent to client (by default) [=client_min_messages]
        return logging.DEBUG
    elif severity_nonlocalized == 'INFO': # always sent to client
        return logging.INFO
    elif severity_nonlocalized == 'WARNING': # sent to client (by default) [=log_min_messages]
        return logging.WARNING
    elif severity_nonlocalized in ['ERROR', 'FATAL']: # sent to client
        return logging.ERROR
    elif severity_nonlocalized in 'PANIC': # sent to client
        return logging.CRITICAL
    else:
        return logging.ERROR
