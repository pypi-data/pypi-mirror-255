from __future__ import annotations

import logging
from subprocess import CompletedProcess, SubprocessError
from typing import Any

from .colors import Colors

logger = logging.getLogger(__name__)



def get_exit_code(return_value: Any) -> int:    
    if not isinstance(return_value, int):
        return_value = 0 if return_value is None or return_value is True else 1
    return return_value


def check_completed_subprocess(cp: CompletedProcess, logger: logging.Logger = None, *, label: str = None, level: int|str = None, accept_returncode: int|list[int]|bool = False, accept_stdout: bool = False, accept_stderr: bool = False, maxlen: int = 200):
    if not label:
        label = cp.args[0]

    if not logger and level is not None:
        logger = globals()["logger"]
    elif logger and level is None:
        level = logging.ERROR


    def is_returncode_issue(returncode: int):
        if accept_returncode is True:
            return False
        elif isinstance(accept_returncode, int):
            return returncode != accept_returncode
        elif isinstance(accept_returncode, (list,tuple)):
            return returncode not in accept_returncode
        else:
            return returncode != 0
    

    def extract_stream(content: str|bytes, name: str, color: str):
        if not isinstance(content, str):
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                content = content.decode('cp1252')
        
        data = content.strip()
        if maxlen and len(data) > maxlen:
            data = data[0:maxlen] + '…'

        result = ''
        for line in data.splitlines():
            result += f"\n{color}[{label} {name}]{Colors.RESET} {line}"
        return result
    

    issue = False

    if is_returncode_issue(cp.returncode):
        message = f"{label} returned {Colors.YELLOW}code {cp.returncode}{Colors.RESET}"
        issue = True
    else:
        message = f"{label} returned {Colors.CYAN}code {cp.returncode}{Colors.RESET}"
    

    result = extract_stream(cp.stdout, 'stdout', Colors.CYAN if accept_stdout else Colors.YELLOW)
    if result:
        message += result
        if not accept_stdout:
            issue = True

    result = extract_stream(cp.stderr, 'stderr', Colors.CYAN if accept_stderr else Colors.YELLOW)
    if result:
        message += result
        if not accept_stderr:
            issue = True

    if issue:
        if logger:
            logger.log(level, message)
        else:
            raise SubprocessError(message)
    else:
        if logger:
            logger.log(logging.DEBUG, message)

    return issue
