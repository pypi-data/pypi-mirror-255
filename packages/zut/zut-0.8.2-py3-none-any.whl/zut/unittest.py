from __future__ import annotations
from pathlib import Path
from unittest import TestProgram

class StartTestProgram(TestProgram):
    """
    A test program starting tests discovery at the given directory (instead of the default `.`).

    Usage example (in root `test.py` executable file):

    ```
    #!/usr/bin/env python3
    from zut.unittest import StartTestProgram, Path
    start = Path(__file__).parent.joinpath('tests')
    StartTestProgram(start)
    ```

    """
    def __init__(self, start: str|Path, module=None, **kwargs):
        self._start = start
        super().__init__(module=module, **kwargs)
        
    @property
    def start(self):
        return self._start
    
    @start.setter
    def start(self, value):
        pass # ignore values set by default TestProgram ('.')
