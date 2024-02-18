from __future__ import annotations
import inspect
import os
from pathlib import Path
from zut.text import skip_utf8_bom
from django.db.migrations import RunSQL

SQL_UTILS_ROOT = Path(__file__).parent.parent.joinpath("db", "sql-utils")

def get_sql_migration_operations(directory: os.PathLike = None, vars: dict = None):
    def get_ordered_files(directory: os.PathLike, *, ext: str = None, recursive: bool = False) -> list[Path]:
        if not isinstance(directory, Path):
            directory = Path(directory)

        if ext and not ext.startswith('.'):
            ext = f'.{ext}'

        def generate(directory: Path):
            for path in sorted(directory.iterdir(), key=lambda entry: (0 if entry.is_dir() else 1, entry.name)):
                if path.is_dir():
                    if recursive:
                        yield from generate(path)
                elif not ext or path.name.lower().endswith(ext):
                    yield path

        return [ path for path in generate(directory) ]


    def get_sql_and_reverse_sql(file: os.PathLike):
        sql = None
        reverse_sql = None

        with open(file, 'r', encoding='utf-8') as fp:
            skip_utf8_bom(fp)

            while line := fp.readline():
                if vars:
                    for name, value in vars.items():
                        line = line.replace("{"+name+"}", value)

                if reverse_sql is None:
                    # search !reverse mark
                    stripped_line = line = line.strip()
                    if stripped_line.startswith('--') and stripped_line.lstrip(' -\t').startswith('!reverse'):
                        reverse_sql = line
                    else:
                        sql = (sql + '\n' if sql else '') + line
                else:
                    reverse_sql += '\n' + line

        return sql, reverse_sql


    if directory is None:
        calling_module = inspect.getmodule(inspect.stack()[1][0])
        calling_file = Path(calling_module.__file__)
        directory = calling_file.parent.joinpath(calling_file.stem)

    operations = []

    for path in get_ordered_files(directory, ext='.sql', recursive=True):
        sql, reverse_sql = get_sql_and_reverse_sql(path)
        operations.append(RunSQL(sql, reverse_sql))

    return operations

def get_pg_utils_migration_operation():
    return RunSQL(SQL_UTILS_ROOT.joinpath("pg.sql").read_text('utf-8'))
