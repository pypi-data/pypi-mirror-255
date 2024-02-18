from __future__ import annotations
import ctypes
import sys


class Colors:
    """ ANSI color codes """
    RESET = "\033[0m"

    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[0;37m"
    GRAY = "\033[0;90m"
    BOLD_RED = '\033[0;1;31m'

    # Platform/terminal specifics
    DISABLED = False
    if not (sys.stdout.isatty() and sys.stderr.isatty()):
        # Disable colors if we don't write to a terminal
        DISABLED = True
        for _ in dir():
            if isinstance(_, str) and _[0] != "_" and _ not in ['DISABLED']:
                locals()[_] = ""
    
    elif sys.platform == 'win32':
        # Set Windows console in VT mode
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        del kernel32
