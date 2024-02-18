"""
Add and execute commands easily, based on argparse.
Usefull for non-Django applications.
For Django applications, use including command management instead.
"""
from __future__ import annotations
from contextlib import nullcontext
import inspect

import logging
from argparse import Action, ArgumentParser, Namespace, RawTextHelpFormatter, _SubParsersAction
from configparser import _UNSET
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
import sys
from types import FunctionType, GeneratorType, ModuleType
from typing import Any, Callable, Iterable, Sequence

from .logging import configure_logging
from .process import get_exit_code

logger = logging.getLogger(__name__)


def add_func_command(parser: ArgumentParser|_SubParsersAction[ArgumentParser], handle: FunctionType, add_arguments: FunctionType = None, *, name: str = None, doc: str = None, defaults: dict[str,Any] = {}):
    """
    Add the given function as a subcommand of the parser.
    """
    if name is None:
        name = handle.__name__
    if doc is None:
        doc = handle.__doc__

    subparsers = _get_subparsers(parser)
    cmdparser = subparsers.add_parser(name, help=get_help_text(doc), description=get_description_text(doc), formatter_class=RawTextHelpFormatter)
    cmdparser.set_defaults(handle=handle, **defaults)

    if add_arguments:
        add_arguments(cmdparser)

    return cmdparser


def add_module_command(parser: ArgumentParser|_SubParsersAction[ArgumentParser], module: str|ModuleType, *, name: str = None, doc: str = None, defaults: dict[str,Any] = {}):
    """
    Add the given module as a subcommand of the parser.
    
    The command function must be named `handler` and the arguments definition function, if any, must be named `add_arguments`.
    """
    if not isinstance(module, ModuleType):
        module = import_module(module)

    if name is None:
        module_basename = module.__name__.split('.')[-1]
        name = module_basename.split('.')[-1]
        if name.endswith('cmd') and len(name) > len('cmd'):
            name = name[0:-len('cmd')]

    if hasattr(module, 'Command'): # like Django Command
        cmdcls = module.Command
        handle = cmdcls  # use the Command class as "handle" - the runner will have to instanciate the class and call the class' handle
        add_arguments = getattr(cmdcls, 'add_arguments', None)        
        doc = getattr(cmdcls, 'help', None) or cmdcls.__doc__

    else:
        try:
            handle = getattr(module, 'handle')

        except AttributeError:
            try:
                handle = getattr(module, name)
            except AttributeError:
                raise ValueError(f"cannot use module {module.__name__} as a command: no function named 'handle' or '{name}'")

        add_arguments = getattr(module, 'add_arguments', None)
        
    if doc is None and module.__doc__:
        doc = module.__doc__
    
    add_func_command(parser, handle, add_arguments=add_arguments, name=name, doc=doc, defaults=defaults)


def add_package_commands(parser: ArgumentParser|_SubParsersAction[ArgumentParser], package: str):
    """
    Add all modules in the given package as subcommands of the parser.
    """
    package_spec = find_spec(package)
    if not package_spec:
        raise KeyError(f"package not found: {package}")
    if not package_spec.origin:
        raise KeyError(f"not a package: {package} (did you forget __init__.py ?)")
    package_path = Path(package_spec.origin).parent
    
    for module_path in sorted(package_path.iterdir()):
        if module_path.is_dir() or module_path.name.startswith("_") or not module_path.name.endswith(".py"):
            continue

        module = module_path.stem
        add_module_command(parser, f"{package}.{module}")


def _get_subparsers(parser: ArgumentParser) -> _SubParsersAction[ArgumentParser]:
    """
    Get or create the subparsers object associated with the given parser.
    """
    if isinstance(parser, _SubParsersAction):
        return parser
    elif parser._subparsers is not None:
        return next(filter(lambda action: isinstance(action, _SubParsersAction), parser._subparsers._actions))
    else:
        return parser.add_subparsers(title='commands')


def get_help_text(docstring: str):
    if docstring is None:
        return None
    
    docstring = docstring.strip()
    try:
        return docstring[0:docstring.index('\n')].strip()
    except:
        return docstring


def get_description_text(docstring: str):
    if docstring is None:
        return None
    
    docstring = docstring.replace('\t', ' ')
    lines = docstring.splitlines(keepends=False)

    min_indent = None
    for line in lines:
        lstriped_line = line.lstrip()
        if lstriped_line:
            indent = len(line) - len(lstriped_line)
            if min_indent is None or min_indent > indent:
                min_indent = indent
    
    description = None
    for line in lines:
        description = (description + '\n' if description else '') + line[min_indent:]

    return description


class CommandManager:
    def __init__(self, main_module: ModuleType|str = None, *, prog: str = None, version: str = None, add_arguments: Callable[[ArgumentParser]] = None, default_handle: Callable = None, runner: Callable = None, doc: str = None):
        self._registered_resources: dict[str,CommandResource] = {}
        self._used_resources: list[CommandResource] = []
        self._args: dict[str,Any] = None

        if main_module or prog or version or add_arguments or default_handle or runner or doc:
            self._prepare(main_module, prog, version, add_arguments, default_handle, runner, doc)


    def _prepare(self, main_module: ModuleType|str, prog: str, version: str, add_arguments: Callable[[ArgumentParser]], default_handle: Callable, runner: Callable, doc: str = None):
        """
        Prepare entry points. May be done in `__init__` (simple because applicable whatever the usage)
        or in the usage function, `main` for example (sometimes required to avoid circular dependencies when passing the root module in `__init__`).
        """
        if hasattr(self, 'main_module'):
            raise ValueError(f"main_module already provided")
        
        if isinstance(main_module, str):
            main_module = import_module(main_module)

        self.main_module = main_module if main_module else inspect.getmodule(inspect.stack()[2][0])
        self.root_module = import_module(".", package=self.main_module.__package__)

        if prog:
            self.prog = prog
        else:
            self.prog = self.root_module.__name__
            if self.prog.endswith('.commands'):
                self.prog = self.prog[0:-len('.commands')]

        self.version = version
        
        # Determine entry points
        self.add_arguments = add_arguments or getattr(self.main_module, 'add_arguments', None)
        self.default_handle = default_handle or getattr(self.main_module, 'handle', None)
        self.runner = runner or getattr(self.main_module, 'runner', None)
        self.doc = doc or self.main_module.__doc__ or self.root_module.__doc__


    def main(self, main_module: ModuleType|str = None, prog: str = None, version: str = None, add_arguments: Callable[[ArgumentParser]] = None, default_handle: Callable = None, runner: Callable = None, doc: str = None):
        """
        A default `main` function for applications.

        Commands are defined in the package's __main__ module using `handle` and `add_arguments` functions.
        """
        if not hasattr(self, 'main_module') or main_module or prog or version or add_arguments or default_handle or runner or doc:
            self._prepare(main_module, prog, version, add_arguments, default_handle, runner, doc)

        configure_logging(prog=prog)

        # Build argument parser
        parser = ArgumentParser(prog=self.prog, description=get_description_text(self.doc), formatter_class=RawTextHelpFormatter)
        parser.add_argument('--version', action='version', version=f"{self.prog} {self.version or ''}")

        if self.add_arguments:
            self.add_arguments(parser)

        # Parse command line
        namespace = parser.parse_args()
        args = vars(namespace)
        handle = args.pop('handle', self.default_handle)

        # Run command
        r = self.run_command(handle, **args)
        exit(r)


    def create_django_command(self, main_module: ModuleType|str = None, *, prog: str = None, version: str = None, add_arguments: Callable[[ArgumentParser]] = None, default_handle: Callable = None, runner: Callable = None, doc: str = None):
        """
        Create a Django management command.
        """
        from django.core.management import BaseCommand

        if not hasattr(self, 'main_module') or main_module or prog or version or add_arguments or default_handle or runner or doc:
            self._prepare(main_module, prog, version, add_arguments, default_handle, runner, doc)

        _prog_and_version = f"{self.prog} {self.version or ''}"

        class Command(BaseCommand):
            help = get_help_text(self.doc)
            
            def get_version(self):
                return _prog_and_version

            def add_arguments(self2, parser):
                if self.add_arguments:
                    self.add_arguments(parser)

            def handle(self2, handle=None, **args):
                args.pop('verbosity', None)
                args.pop('settings', None)
                args.pop('pythonpath', None)
                args.pop('traceback', None)
                args.pop('no_color', None)
                args.pop('force_color', None)
                args.pop('skip_checks', None)

                if handle is None and self.default_handle:
                    handle = self.default_handle

                return self.run_command(handle, **args)

        return Command


    def run_command(self, handle: Callable, **args):
        if not handle:
            logger.error("no command given")
            return 1
        
        with self.prepare_args(args, handle) as args:
            # Run command
            try:
                if self.runner:
                    r = self.runner(handle, args)
                else:            
                    r = handle(**args)

                r = get_exit_code(r)
            except BaseException as err:
                message = str(err)
                logger.exception(f"exiting on {type(err).__name__}{f': {message}' if message else ''}")
                r = 1
            return r


    def register_resource(self, dest: str, builder: Callable[[str],Any], *, metavar: str = None, default: str = None, choices: Iterable = None, help: str = None):
        """
        Register a resource.
        - `dest`: name of the function parameter.
        """
        if dest in self._registered_resources:
            raise ValueError(f"resource already defined: {dest}")
        
        self._registered_resources[dest] = CommandResource(dest, builder, metavar=metavar, default=default, choices=choices, help=help)


    def get_resource_action(self, dest: str):
        return self._registered_resources[dest].get_action()
    

    def get_resource_instance(self, dest: str, arg: Any = _UNSET):
        resource = self._registered_resources[dest]

        if arg in resource._built:
            return resource._built[arg]
        
        elif len(resource._built) == 1:
            return next(iter(resource._built.values()))
        
        elif not resource._built:
            raise ValueError(f"resource \"{dest}\" not built yet")
        
        else:
            raise ValueError(f"several resource \"{dest}\" built")
    

    def prepare_args(self, args: dict, handle: FunctionType):
        if isinstance(args, Namespace):
            self._args = vars(args)
        else:
            self._args = args

        func_parameters = inspect.signature(handle).parameters
        
        for dest, resource in self._registered_resources.items():
            used = False
            
            if dest in self._args:
                instance = resource.get_or_build(self._args[dest])
                self._args[dest] = instance
                used = True

            elif dest in func_parameters:
                instance = resource.get_or_build(_UNSET)
                self._args[dest] = instance
                used = True
            
            if used and resource not in self._used_resources:
                self._used_resources.append(resource)
        
        return self


    def __enter__(self):
        if self._args is None:
            raise ValueError('prepare_args must be called first')
        return self._args


    def __exit__(self, exc_type, exc_value, traceback):
        for instance in self._used_resources:
            instance.close(exc_type, exc_value, traceback)


def main():
    """
    A default `main` function for applications.

    Commands are defined in the package's __main__ module using `handle` and `add_arguments` functions.
    """
    main_module = inspect.getmodule(inspect.stack()[1][0])
    CommandManager().main(main_module=main_module)


class CommandResource:
    def __init__(self, dest: str, builder: Callable[...,Any], *, metavar: str = None, default: str = None, choices: Iterable = None, help: str = None):
        self.dest = dest
        self.builder = builder
        self.metavar = metavar
        self.default = default
        self.choices = choices
        self.help = help
        self._built: dict[Any,Any] = {}


    def get_action(self):
        class ResourceAction(Action):
            def __init__(a_self, option_strings, **kwargs):            
                kwargs['dest'] = self.dest
                if not 'default' in kwargs and self.default is not None:
                    kwargs['default'] = self.default
                if not 'choices' in kwargs and self.choices is not None:
                    kwargs['choices'] = self.choices
                if not 'metavar' in kwargs and self.metavar is not None:
                    kwargs['metavar'] = self.metavar
                if not 'help' in kwargs and self.help is not None:
                    kwargs['help'] = self.help
                super().__init__(option_strings, **kwargs)

            def __call__(a_self, parser: ArgumentParser, namespace: Namespace, values: str | Sequence[Any] | None, option_string: str | None = None):
                setattr(namespace, self.dest, values)
        
        return ResourceAction


    def get_or_build(self, arg_value = _UNSET):
        if not arg_value in self._built:
            if arg_value is not _UNSET:
                result = self.builder(arg_value)
            elif self.default is not _UNSET:
                result = self.builder(self.default)
            else:
                result = self.builder()

            if hasattr(result, '__enter__'):
                result.__enter__()
            if isinstance(result, GeneratorType):
                result = [instance for instance in result]
            self._built[arg_value] = result
        
        return self._built[arg_value]
        

    def close(self, exc_type, exc_value, traceback):
        def close_instance(instance):
            # actual closing
            if hasattr(instance, '__exit__'):
                instance.__exit__(exc_type, exc_value, traceback)
            elif hasattr(instance, 'close'):
                instance.close()

        def close_list(instances: list):
            for instance in instances:
                if isinstance(instance, list):
                    close_list(instance)
                else:
                    close_instance(instance)

        def close_dict(instances: dict):
            for instance in instances.values():
                if isinstance(instance, list):
                    close_list(instance)
                else:
                    close_instance(instance)

        close_dict(self._built)
