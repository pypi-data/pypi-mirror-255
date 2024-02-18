
import argparse
import json5
from typing import Any, NoReturn, IO, Dict, Optional, Callable
from Shared import certoraUtils as Util
from enum import auto
from dataclasses import dataclass, field


APPEND = 'append'
STORE_TRUE = 'store_true'
VERSION = 'version'
SINGLE_OR_NONE_OCCURRENCES = '?'
MULTIPLE_OCCURRENCES = '*'
ONE_OR_MORE_OCCURRENCES = '+'


def default_validation(x: Any) -> Any:
    return x


class UniqueStore(argparse.Action):
    """
    This class makes the argparser throw an error for a given flag if it was inserted more than once
    """

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Any,  # type: ignore
                 option_string: str) -> None:
        if getattr(namespace, self.dest, self.default) is not self.default:
            parser.error(f"{option_string} appears several times.")
        setattr(namespace, self.dest, values)


class NotAllowed(argparse.Action):
    """
    This class makes the argparser throw an error for a given flag if it was set in CLI (can be set using conf file)
    """

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Any,  # type: ignore
                 option_string: str) -> None:

        parser.error(f"{option_string} cannot be set in command line only in a conf file.")


class CertoraArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> NoReturn:
        error_message = f'Please remember, CLI flags should be preceded with double dashes!{Util.NEW_LINE}' \
                        'For more help run the tool with the option --help'
        prefix = 'unrecognized arguments: '
        if message.startswith(prefix):
            flag = message[len(prefix):].split()[0]
            if len(flag) > 1 and flag[0] == '-' and flag[1] != '-':
                raise Util.CertoraUserInputError(f"{prefix} {flag}{Util.NEW_LINE}{error_message}")
        raise Util.CertoraUserInputError(message)


def validate_for_conf_file_duplicates(conf_file: IO[str]) -> None:

    def detect_duplicates(ordered_pairs: Dict) -> None:
        result: Dict[str, Any] = {}
        for key, val in ordered_pairs:
            if key in result:
                vals = f"values: '{val}' and {result[key]}" if val and result[key] else ""
                raise Util.CertoraUserInputError(f"Duplicate key specified for key {key}. {vals}")
            result[key] = val

    json5.load(conf_file, object_pairs_hook=detect_duplicates)
    conf_file.seek(0)


class AttrArgType(Util.NoValEnum):
    STRING = auto()
    BOOLEAN = auto()
    LIST = auto()
    INT = auto()
    MAP = auto()


class BaseAttribute(Util.NoValEnum):
    pass


@dataclass
class BaseArgument:
    flag: Optional[str] = None  # override the 'default': option name
    attr_validation_func: Callable = default_validation
    help_msg: str = argparse.SUPPRESS
    # args for argparse's add_attribute passed as is
    argparse_args: Dict[str, Any] = field(default_factory=dict)
    arg_type: AttrArgType = AttrArgType.STRING
