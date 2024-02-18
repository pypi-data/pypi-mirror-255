import os
from io import IOBase
from django.db import connection, models, transaction
from zut.db import get_db_adapter

@transaction.atomic
def load_model_from_csv(source: os.PathLike|IOBase, model: type[models.Model], columns: list[str] = None, encoding: str = 'utf-8', *,  truncate: bool = False, noheaders: bool = False, delimiter: str = None, quotechar: str = None, nullval: str = None):
    with get_db_adapter(connection) as db:
        return db.load_from_csv(source, model._meta.db_table, columns, encoding=encoding, truncate=truncate, noheaders=noheaders, delimiter=delimiter, quotechar=quotechar, nullval=nullval)
