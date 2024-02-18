from __future__ import annotations
from io import IOBase
from atexit import register as register_atexit
import logging
import os
from pathlib import Path
import sys
from typing import Any, Callable
from .. import files

from .utils import get_inout_name, normalize_inout

logger = logging.getLogger(__name__)


class OutFile:
    def __init__(self, out: str|Path|IOBase|None = None, *, dir: str|Path|None = None, title: str|None = None, append: bool = False, encoding: str = 'utf-8-sig', newline: str = None, atexit: bool|Callable = None, **kwargs):
        from .OutExcel import OutExcel

        self.out = normalize_inout(out, dir=dir, title=title, **kwargs)
        self.name = get_inout_name(self.out)
        
        self._title = title
        self._append = append
        self._encoding = encoding
        self._newline = newline

        self.file: IOBase = None
        self._must_close_file: bool = True

        if atexit == '__if_excel__':
            self.atexit = isinstance(self, OutExcel)
        else:
            self.atexit = atexit


    # -------------------------------------------------------------------------
    # Enter/exit context
    #

    def __enter__(self) -> IOBase:        
        self._open_file()

        if self.atexit:
            if callable(self.atexit):
                self.atexit(self)
            else:
                register_atexit(self.end)

        return self.file


    def __exit__(self, exc_type = None, exc_val = None, exc_tb = None):
        if not self.atexit:
            self.end()

            
    def end(self):
        """
        This method is automatically executed when context ends (__exit__), except if `atexit` is truthy.
        """
        self._close_file()


    # -------------------------------------------------------------------------
    # Open file
    #

    def _open_file(self):
        self._print_title()

        if self.out in [sys.stdout, sys.stderr]:
            self.file = self.out
            self._must_close_file = False
            
        else:
            if isinstance(self.out, IOBase):
                self.file = self.out
                self._must_close_file = False
            
            else:
                parent = files.dirname(self.out)
                if parent and not files.exists(parent):
                    files.makedirs(parent)

                self.file = files.open(self.out, 'a' if self._append else 'w', newline=self._newline, encoding=self._encoding)
                self._must_close_file = True


    def _print_title(self):
        if self._title is False:
            return
        if self.out == os.devnull:
            return

        if self.out in [sys.stdout, sys.stderr] and self.out.isatty():
            if self._title:
                print(f"\n########## {self._title} ##########\n", file=self.out)
        else:
            logger.info(f"{'append' if self._append else 'export'}{f' {self._title}' if self._title else ''} to {self.name}")


    # -------------------------------------------------------------------------
    # Close file
    #    

    def _close_file(self):
        if self.file and self._must_close_file:
            self.file.close()
