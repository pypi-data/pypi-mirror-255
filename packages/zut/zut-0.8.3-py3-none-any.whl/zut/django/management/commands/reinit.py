from __future__ import annotations
import logging
from django.conf import settings
from django.db import connection
from django.core.management import base, call_command
from ....db import get_db_adapter

logger = logging.getLogger(__name__)


class Command(base.BaseCommand):
    REINIT_POST_COMMANDS: list[str|list[str]] = getattr(settings, "REINIT_POST_COMMANDS", [])

    def add_arguments(self, parser):
        parser.add_argument("-d", "--drop", dest="schema", action="store_const", const="drop", help="drop existing objects and data")
        parser.add_argument("-b", "--bak", dest="schema", action="store_const", const="bak", help="move existing objects and data to schema \"bak\"")
        parser.add_argument("-t", "--bak-to", dest="schema", help="move existing objects and data to the given schema")
        parser.add_argument("-x", "--exclude", nargs='*', dest="exclude_apps", metavar='apps', help="label of apps to exclude from migrations remaking")
        parser.add_argument("apps", nargs="*", help="label of apps for which migrations are remade")


    def handle(self, schema: str = None, apps: list[str] = [], exclude_apps: list[str] = None, **kwargs):
        if not settings.DEBUG:
            raise ValueError("reinit may be used only in DEBUG mode")
        if not schema:
            raise ValueError("please confirm what to do with current data: --drop, --bak or --bak-to")

        db = get_db_adapter(settings.DATABASES["default"])

        if schema == "drop":
            db.drop_all()
        else:
            db.move_all_to_new_schema(schema)

        call_command("remakemigrations", *apps, exclude_apps=exclude_apps)

        logger.info("migrate")
        call_command("migrate")

        for post_command in self.REINIT_POST_COMMANDS:
            if not isinstance(post_command, list):
                post_command = [post_command]
            logger.info(' '.join(post_command))
            call_command(*post_command)
