from __future__ import annotations
import os
import re

import sys
from configparser import ConfigParser, _UNSET, NoOptionError, NoSectionError
from pathlib import Path
from typing import TypeVar

from .text import skip_utf8_bom
from .types import convert

T = TypeVar('T')


def get_env_config(name: str, fallback: str = _UNSET, type: type[T] = str) -> T:
    """
    Get a configuration value from environment variables.
    """
    if name in os.environ:
        value = os.environ[name]

    else:
        if fallback is _UNSET:
            raise ConfigurationError(name, "environment variable")
        value = fallback
    
    if type != str:
        return convert(value, type)
    else:
        return value


def get_secret_config(name: str, fallback: str = _UNSET, type: type[T] = str):
    """
    Get a configuration value from secret files.
    """
    name = name.lower()

    if os.path.exists(f"secrets/{name}.txt"): # for local and/or development environment
        value = _read_file_and_rstrip_newline(f"secrets/{name}.txt")
    
    elif os.path.exists(f"/run/secrets/{name}"): # see: https://docs.docker.com/compose/use-secrets/
        value = _read_file_and_rstrip_newline(f"/run/secrets/{name}")

    else:        
        if fallback is _UNSET:
            raise ConfigurationError(name, "secret")
        value = fallback
        
    if type != str:
        return convert(value, type)
    else:
        return value


class ConfigurationError(Exception):
    def __init__(self, name: str, nature: str = "option"):
        message = f"{nature} {name} not configured"
        super().__init__(message)
        self.name = name
        self.nature = nature


def get_config_parser(prog: str) -> ExtendedConfigParser:
    """
    A function to search for configuration files in some common paths.
    """
    if not prog:
        raise ValueError("prog required")
        # NOTE: we should not try to determine prog here: this is too dangerous (invalid/fake configuration files could be loaded by mistake)

    parser = ExtendedConfigParser()

    parser.read([
        # System configuration
        Path(f'C:/ProgramData/{prog}/{prog}.conf' if sys.platform == 'win32' else f'/etc/{prog}/{prog}.conf').expanduser(),
        Path(f'C:/ProgramData/{prog}.conf' if sys.platform == 'win32' else f'/etc/{prog}.conf').expanduser(),
        # User configuration
        Path(f'~/.config/{prog}/{prog}.conf').expanduser(),
        Path(f'~/.config/{prog}.conf').expanduser(),
        # Local configuration
        "local.conf",
    ], encoding='utf-8')

    return parser


class ExtendedConfigParser(ConfigParser):
    def getsecret(self, section: str, option: str, *, raw=False, vars=None, fallback: str = _UNSET) -> str:
        """
        If option not found, will also try to read the value from:
        - A file named `secrets/{section}_{option}.txt` if exists (usefull for local/development environment).
        - A file named `/run/secrets/{section}_{option}` if exists (usefull for Docker secrets - see https://docs.docker.com/compose/use-secrets/).
        - The file indicated by option `{option}_file` (usefull for password files).
        """
        result = self.get(section, option, raw=raw, vars=vars, fallback=None)

        if result is not None:
            return result

        secret_name = f'{section}_{option}'.replace(':', '-')

        # try local secret
        secret_path = f'secrets/{secret_name}.txt'
        if os.path.exists(secret_path):
            return _read_file_and_rstrip_newline(secret_path)

        # try Docker-like secret
        secret_path = f'/run/secrets/{secret_name}'
        if os.path.exists(secret_path):
            return _read_file_and_rstrip_newline(secret_path)

        # try file
        path = self.get(section, f'{option}_file', raw=raw, vars=vars, fallback=None)
        if path is not None:
            return _read_file_and_rstrip_newline(path)
        
        if fallback is _UNSET:
            raise NoOptionError(option, section)
        else:
            return fallback


    def getlist(self, section: str, option: str, *, raw=False, vars=None, delimiter=None, fallback: list[str] = _UNSET) -> list[str]:
        values_str = self.get(section, option, raw=raw, vars=vars, fallback=fallback)
        if not isinstance(values_str, str):
            return values_str # fallback
        
        if delimiter:
            if not values_str:
                return []
            
            values = []
            for value in values_str.split(delimiter):
                value = value.strip()
                if not value:
                    continue
                values.append(value)

            return values
        else:
            return convert(values_str, list)


def _read_file_and_rstrip_newline(path: os.PathLike):
    with open(path, 'r', encoding='utf-8') as fp:
        skip_utf8_bom(fp)
        value = fp.read()
        return value.rstrip('\r\n')
