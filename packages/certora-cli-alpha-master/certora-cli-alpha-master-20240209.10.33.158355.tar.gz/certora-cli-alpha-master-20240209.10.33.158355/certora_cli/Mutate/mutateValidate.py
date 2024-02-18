from pathlib import Path
import json5
import sys

scripts_dir_path = Path(__file__).parent.resolve()
sys.path.insert(0, str(scripts_dir_path))

from Mutate import mutateAttribute as Attr
from Shared import certoraAttrUtil as AttrUtil
from Shared import certoraUtils as Util
from typing import Tuple, Any
from Mutate import mutateApp as App
from Mutate import mutateConstants as Constants


class MutateValidator:
    def __init__(self, mutateApp: App.MutateApp):
        self.mutateApp = mutateApp

    def validate(self) -> None:
        self.validate_args()
        self.validate_server()
        self.set_defaults()

    def validate_args(self) -> None:

        for arg in Attr.MutateAttribute:
            attr = getattr(self.mutateApp, str(arg), None)
            if attr is None or (attr is False and AttrUtil.AttrArgType.BOOLEAN):
                continue

            if arg.value.arg_type == AttrUtil.AttrArgType.STRING:
                self.validate_type_string(arg)
            elif arg.value.arg_type == AttrUtil.AttrArgType.BOOLEAN:
                self.validate_type_boolean(arg)
            elif arg.value.arg_type == AttrUtil.AttrArgType.INT:
                self.validate_type_int(arg)
            elif arg.value.arg_type == AttrUtil.AttrArgType.MAP:
                self.validate_type_any(arg)
            else:
                raise RuntimeError(f"{attr.value.arg_type} - unknown arg type")

    def validate_type_string(self, attr: Attr.MutateAttribute) -> None:
        key, value = self.__get_key_and_value(attr)

        if value is None:
            raise RuntimeError(f"calling validate_type_string with null value {key}")
        if not isinstance(value, str) and not isinstance(value, Path):
            raise Util.CertoraUserInputError(f"value of {key} {value} is not a string")
        attr.validate_value(str(value))

    def validate_type_any(self, attr: Attr.MutateAttribute) -> None:
        key, value = self.__get_key_and_value(attr)

        if value is None:
            raise RuntimeError(f"calling validate_type_any with null value {key}")
        attr.validate_value(value)

    def validate_type_int(self, attr: Attr.MutateAttribute) -> None:
        key, value = self.__get_key_and_value(attr)

        if value is None:
            raise RuntimeError(f"calling validate_type_string with null value {key}")
        if not isinstance(value, int):
            raise Util.CertoraUserInputError(f"value of {key} {value} is not an integer")
        attr.validate_value(str(value))

    def validate_type_boolean(self, attr: Attr.MutateAttribute) -> None:
        key, value = self.__get_key_and_value(attr)

        if value is None:
            raise RuntimeError(f"{key}: calling validate_type_boolean with None")
        elif type(value) is list and len(value) == 0:
            setattr(self.mutateApp, key, True)
        elif value not in [True, False]:
            raise Util.CertoraUserInputError(f"value of {key} {value} is not a boolean (true/false)")

    def __get_key_and_value(self, attr: Attr.MutateAttribute) -> Tuple[str, Any]:
        key = str(attr)
        value = getattr(self.mutateApp, key, None)
        return key, value

    def validate_server(self) -> str:
        """
        If given a server, it is taken.
        Otherwise, computes from either the conf file or the orig run link.
        """
        # default production
        default = Constants.PRODUCTION
        if self.mutateApp.server:
            return self.mutateApp.server
        elif self.mutateApp.prover_conf is not None:
            # read the conf and try to get server configuration
            with open(self.mutateApp.prover_conf, 'r') as conf_file:
                conf_obj = json5.load(conf_file)
            if Constants.SERVER in conf_obj:
                return conf_obj[Constants.SERVER]
            else:
                return default

        elif self.mutateApp.orig_run is not None:
            if Constants.STAGING_DOTCOM in self.mutateApp.orig_run:
                return Constants.STAGING
            elif Constants.PROVER_DOTCOM in self.mutateApp.orig_run:
                return default
            elif Constants.DEV_DOTCOM in self.mutateApp.orig_run:
                return Constants.DEV
            else:
                raise Util.CertoraUserInputError(f"{self.mutateApp.orig_run} link is neither for staging "
                                                 f"not production.")
        else:
            return default

    def set_defaults(self) -> None:
        if not self.mutateApp.orig_run_dir:
            self.mutateApp.orig_run_dir = Path(Constants.CERTORA_MUTATE_SOURCES)
        if not self.mutateApp.dump_failed_collects:
            self.mutateApp.dump_failed_collects = Constants.DEFAULT_DUMP_FAILED_COLLECTS
        if not self.mutateApp.collect_file:
            self.mutateApp.collect_file = Constants.DEFAULT_COLLECT_FILE
        if not self.mutateApp.poll_timeout:
            self.mutateApp.poll_timeout = Constants.DEFAULT_POLL_TIMEOUT_IN_SECS
        if not self.mutateApp.max_timeout_attempts_count:
            self.mutateApp.max_timeout_attempts_count = Constants.DEFAULT_MAX_TIMEOUT_ATTEMPTS_COUNT
        if not self.mutateApp.request_timeout:
            self.mutateApp.request_timeout = Constants.DEFAULT_REQUEST_TIMEOUT_IN_SECS
        if not self.mutateApp.ui_out:
            self.mutateApp.ui_out = Constants.DEFAULT_UI_OUT
