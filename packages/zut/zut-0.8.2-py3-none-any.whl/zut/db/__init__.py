from __future__ import annotations
import re
from urllib.parse import urlparse

from .base import DbAdapter, _get_connection_from_wrapper
from .mssql import MssqlAdapter
from .pg import PgAdapter, Pg2Adapter, pg_notice_handler, Pg2NoticeHandler # not used in this module but added as top-level API


def get_db_adapter_with_schema_and_table(origin) -> tuple[DbAdapter, str, str]:
    if isinstance(origin, str):
        if origin.startswith('db:'):
            origin = origin[3:]

        r = urlparse(origin)

        if r.scheme in ['postgresql', 'postgres', 'pg']:
            if PgAdapter.is_available():
                adapter = PgAdapter
            elif Pg2Adapter.is_available():
                adapter = Pg2Adapter
            else:
                raise ValueError(f"PgAdapter and Pg2Adapter not available (psycopg missing)")
        elif r.scheme in ['mssql']:
            adapter = MssqlAdapter
        elif r.scheme:
            raise ValueError(f"unsupported db engine: {r.scheme}")
        else:
            raise ValueError(f"invalid db: no scheme in {origin}")
        
        if not adapter.is_available():
            raise ValueError(f"cannot use db {r.scheme} ({adapter.__name__} not available)")
        
        if r.fragment:
            raise ValueError(f"invalid db: unexpected fragment: {r.fragment}")
        if r.query:
            raise ValueError(f"invalid db: unexpected query: {r.query}")
        if r.params:
            raise ValueError(f"invalid db: unexpected params: {r.params}")
        
        m = re.match(r'^/(?P<name>[^/@\:]+)(/((?P<schema>[^/@\:\.]+)\.)?(?P<table>[^/@\:\.]+))?$', r.path)
        if not m:
            raise ValueError(f"invalid db: invalid path: {r.path}")
        
        table = m['table']
        schema = (m['schema'] or adapter.DEFAULT_SCHEMA) if table else None
        
        r = r._replace(path='/'+m['name'])
        return adapter(r.geturl()), schema, table
    
    elif isinstance(origin, dict) and 'ENGINE' in origin: # Django
        engine = origin['ENGINE']
        if engine in ["django.db.backends.postgresql", "django.contrib.gis.db.backends.postgis"]:
            if PgAdapter.is_available():
                return PgAdapter(origin), None, None
            else:
                return Pg2Adapter(origin), None, None
        elif engine in ["mssql"]:
            return MssqlAdapter(origin), None, None
        else:
            raise ValueError(f"invalid db: unsupported django db engine: {engine}")
        
    elif isinstance(origin, DbAdapter):
        return origin, None, None
    
    else: # connection types
        origin = _get_connection_from_wrapper(origin)
        
        type_fullname: str = type(origin).__module__ + '.' + type(origin).__qualname__

        if type_fullname == 'psycopg2.extension.connection':
            return Pg2Adapter(origin), None, None
        elif type_fullname == 'psycopg.Connection':
            return PgAdapter(origin), None, None
        elif type_fullname == 'pyodbc.Connection':
            return MssqlAdapter(origin), None, None

        raise ValueError(f"invalid db: unsupported origin type: {type(origin)}")


def get_db_adapter(origin) -> DbAdapter:
    db, _, _ = get_db_adapter_with_schema_and_table(origin)
    return db
