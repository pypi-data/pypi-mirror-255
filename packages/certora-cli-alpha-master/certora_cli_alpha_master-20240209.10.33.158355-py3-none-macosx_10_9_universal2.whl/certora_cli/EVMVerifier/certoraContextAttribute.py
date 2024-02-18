import logging
import sys
import re
from functools import lru_cache
from dataclasses import dataclass
from enum import unique
from pathlib import Path
from typing import Optional, List
from Shared import certoraAttrUtil as AttrUtil

from Shared import certoraValidateFuncs as Vf
from Shared import certoraUtils as Util
from rich.console import Console
from rich.table import Table
from rich.text import Text


scripts_dir_path = Path(__file__).parent.resolve()  # containing directory
sys.path.insert(0, str(scripts_dir_path))

# logger for issues regarding context
context_logger = logging.getLogger("context")


def validate_prover_args(value: str) -> str:

    strings = value.split()
    for arg in ContextAttribute:
        if arg.value.jar_flag is None:
            continue
        for string in strings:

            if string == arg.value.jar_flag:
                # globalTimeout will get a special treatment, because the actual arg is the wrong one
                if arg.value.jar_flag == ContextAttribute.CLOUD_GLOBAL_TIMEOUT.value.jar_flag:
                    actual_arg = ContextAttribute.GLOBAL_TIMEOUT
                else:
                    actual_arg = arg
                raise Util.CertoraUserInputError(f"Use CLI flag '{actual_arg.get_flag()}' "
                                                 f"instead of 'prover_args' with {string} as value")
    return value


def validate_typechecker_args(value: str) -> str:
    strings = value.split()
    for arg in ContextAttribute:
        if arg.value.typechecker_flag is None:
            continue
        for string in strings:
            if string == arg.value.typechecker_flag:
                raise Util.CertoraUserInputError(f"Use CLI flag '{arg.get_flag()}' "
                                                 f"instead of 'typechecker_args' with {string} as value")
    return value


def parse_struct_link(link: str) -> str:
    search_res = re.search(r'^\w+:([^:=]+)=\w+$', link)
    # We do not require firm form of slot number so we can give more informative warnings
    if search_res is None:
        raise Util.CertoraUserInputError(f"Struct link argument {link} must be of the form contractA:<field>=contractB")
    if search_res[1].isidentifier():
        return link
    try:
        parsed_int = int(search_res[1], 0)  # an integer or a hexadecimal
        if parsed_int < 0:
            raise Util.CertoraUserInputError(f"struct link slot number negative at {link}")
    except ValueError:
        raise Util.CertoraUserInputError(f"Struct link argument {link} must be of the form contractA:number=contractB"
                                         f" or contractA:fieldName=contractB")
    return link


@dataclass
class CertoraArgument(AttrUtil.BaseArgument):
    deprecation_msg: Optional[str] = None
    jar_flag: Optional[str] = None  # the flag that is sent to the jar (if attr is sent to the jar)
    jar_no_value: Optional[bool] = False  # if true, flag is sent with no value
    typechecker_flag: Optional[
        str] = None  # the flag that is sent to the typechecker jar (if attr is sent to the typechecker jar)

    def get_dest(self) -> Optional[str]:
        return self.argparse_args.get('dest')


@unique
class ContextAttribute(AttrUtil.BaseAttribute):
    """
    This enum class must be unique. If 2 args have the same value we add the 'flag' attribute to make sure the hash
    value is not going to be the same

    The order of the attributes is the order we want to show the attributes in argParse's help

    """
    FILES = CertoraArgument(
        attr_validation_func=Vf.validate_input_file,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="contract files for analysis, a conf file or SOLANA_FILE.so",
        flag='files',
        argparse_args={
            'nargs': AttrUtil.MULTIPLE_OCCURRENCES
        }
    )

    VERIFY = CertoraArgument(
        attr_validation_func=Vf.validate_verify_attr,
        arg_type=AttrUtil.AttrArgType.STRING,
        help_msg="Path to The Certora CVL formal specifications file. \n\nFormat: "
                 f"\n\t{Util.text_blue('<contract>:<spec file>')}\n"
                 f"Example: \n\t{Util.text_blue('Bank:specs/Bank.spec')}\n\n"
                 f"spec files suffix must be {Util.text_blue('.spec')}",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    MSG = CertoraArgument(
        attr_validation_func=Vf.validate_msg,
        help_msg="Adds a message description to your run",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    RULE = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        attr_validation_func=Vf.validate_rule_name,
        jar_flag='-rule',
        help_msg="Filters the list of rules/invariants to verify",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    PROTOCOL_NAME = CertoraArgument(
        help_msg="Adds the protocol's name for easy filtering in the dashboard",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    PROTOCOL_AUTHOR = CertoraArgument(
        help_msg="Adds the protocol's author for easy filtering in the dashboard",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    MULTI_ASSERT_CHECK = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_no_value=True,
        jar_flag='-multiAssertCheck',
        help_msg="Checks each assertion statement that occurs in a rule, separately",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    INDEPENDENT_SATISFY = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_no_value=False,
        jar_flag='-independentSatisfies',
        help_msg="Checks each satisfy statement that occurs in a rule while ignoring previous ones.",
        argparse_args={
            'action': AttrUtil.STORE_TRUE,
        }
    )

    SAVE_VERIFIER_RESULTS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_no_value=True,
        jar_flag='-saveVerifierResults',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    INCLUDE_EMPTY_FALLBACK = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-includeEmptyFallback',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    RULE_SANITY = CertoraArgument(
        attr_validation_func=Vf.validate_sanity_value,
        help_msg="Selects the type of sanity check that will be performed during execution",
        jar_flag='-ruleSanityChecks',
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'default': None,  # 'default': when no --rule_sanity given
            'const': Vf.RuleSanityValue.BASIC.name.lower()  # 'default': when empty --rule_sanity is given
        }
    )

    MULTI_EXAMPLE = CertoraArgument(
        attr_validation_func=Vf.validate_multi_example_value,
        help_msg="Sets the required multi example mode",
        jar_flag='-multipleCEX',
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'default': None,  # 'default': when no --multi_example given
            'const': Vf.MultiExampleValue.BASIC.name.lower()
        }
    )

    FUNCTION_FINDER_MODE = CertoraArgument(
        attr_validation_func=Vf.validate_function_finder_mode,
        help_msg="Controls the instrumentation and processing of internal function finders",
        jar_flag='-functionFinderMode',
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'default': None
        }
    )

    SHORT_OUTPUT = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-ciMode',
        help_msg="Reduces verbosity",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    NO_CALLTRACE_STORAGE_INFORMATION = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-noCalltraceStorageInformation',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    CALLTRACE_REMOVE_EMPTY_LABELS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-calltraceRemoveEmptyLabels',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    TYPECHECK_ONLY = CertoraArgument(
        flag='--typecheck_only',
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    SEND_ONLY = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        deprecation_msg="'send_only' is deprecated and is now the default. In CI, use 'wait_for_results false' instead",
        help_msg="Makes the request to the prover but does not wait for verifications results",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    WAIT_FOR_RESULTS = CertoraArgument(
        attr_validation_func=Vf.validate_wait_for_results,
        help_msg="Wait for verification results before terminating the run",
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'default': None,  # 'default': when --wait_for_results was not used
            'const': str(Vf.WaitForResultOptions.ALL)  # when --wait_for_results was used without an argument
        }
    )

    SOLC = CertoraArgument(
        attr_validation_func=Vf.validate_exec_file,
        help_msg="Path to the Solidity compiler executable file",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    SOLC_VIA_IR = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="pass --via-ir flag to solidity compiler",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    SOLC_EXPERIMENTAL_VIA_IR = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="pass --experimental-via-ir flag to solidity compiler",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    SOLC_EVM_VERSION = CertoraArgument(
        help_msg="Intructs the Solidity compiler to use a specific EVM version",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    SOLC_MAP = CertoraArgument(
        attr_validation_func=Vf.validate_solc_map,
        arg_type=AttrUtil.AttrArgType.MAP,
        help_msg="Maps contracts to the appropriate Solidity compiler in case not all contract files are compiled "
                 "with the same Solidity compiler version. \n\nCLI Example: "
                 f"\n\t{Util.text_blue('--solc_map A=solc8.11,B=solc8.9,C=solc7.5')}\n\nJSON Example: "
                 f"\n\t" + Util.text_blue('solc_map: {"A": "solc8.11", "B": "solc8.9", "C": "solc7.5"}'),

        argparse_args={
            'action': AttrUtil.UniqueStore,
            'type': lambda value: Vf.parse_dict('solc_map', value)
            }
    )

    SOLC_ALLOW_PATH = CertoraArgument(
        attr_validation_func=Vf.validate_dir,
        help_msg="Sets the base path for loading Solidity files",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    SOLC_OPTIMIZE = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer_or_minus_1,
        help_msg="Tells the Solidity compiler to optimize the gas costs of the contract for a given number of runs, "
                 "if number of runs is not defined the Solidity compiler default is used",
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'const': '-1'
        }
    )

    SOLC_OPTIMIZE_MAP = CertoraArgument(
        attr_validation_func=Vf.validate_solc_optimize_map,
        arg_type=AttrUtil.AttrArgType.MAP,
        help_msg="Maps contracts to their optimized number of runs in case not all contract files are compiled "
                 "with the same number of runs. \n\nCLI Example: "
                 f"\n\t{Util.text_blue('--solc_map A=200,B=300,C=200')}\n\nJSON Example: "
                 f"\n\t" + Util.text_blue('solc_map: {"A": "200", "B": "300", "C": "200"}'),
        argparse_args={
            'action': AttrUtil.UniqueStore,
            'type': lambda value: Vf.parse_dict('solc_optimize_map', value)
            }
    )

    SOLC_ARGS = CertoraArgument(
        attr_validation_func=Vf.validate_solc_args,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    PACKAGES_PATH = CertoraArgument(
        attr_validation_func=Vf.validate_dir,
        help_msg="Path to a directory including the Solidity packages",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    PACKAGES = CertoraArgument(
        attr_validation_func=Vf.validate_packages,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="Maps packages to their location in the file system",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    OPTIMISTIC_LOOP = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-assumeUnwindCond',
        jar_no_value=True,
        help_msg="Assumes the loop halt conditions hold, after unrolling loops",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    LOOP_ITER = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        jar_flag='-b',
        help_msg="Sets maximum number of loop iterations",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    OPTIMISTIC_HASHING = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Bounds the length of data (with potentially unbounded length) to the value given in "
                 "--hashing_length_bound",
        jar_flag='-optimisticUnboundedHashing',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    OPTIMISTIC_SUMMARY_RECURSION = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="In case of recursion of Solidity functions within a summary, "
                 "assume the recursion limit is never reached",
        jar_flag='-optimisticSummaryRecursion',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    SUMMARY_RECURSION_LIMIT = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        help_msg="In case of recursion of Solidity functions within a summary, "
                 "determines the number of recursive calls we verify for`) ",
        jar_flag='-summaryRecursionLimit',
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    HASHING_LENGTH_BOUND = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        jar_flag='-hashingLengthBound',
        help_msg="Maximum length of otherwise unbounded data chunks that are being hashed",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    METHOD = CertoraArgument(
        jar_flag='-method',
        help_msg="Filters methods to be verified by their signature",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    CACHE = CertoraArgument(
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    SMT_TIMEOUT = CertoraArgument(
        attr_validation_func=Vf.validate_positive_integer,
        jar_flag='-t',
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    LINK = CertoraArgument(
        attr_validation_func=Vf.validate_link_attr,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="Links a slot in a contract with another contract. \n\nFormat: "
                 f"\n\t{Util.text_blue('<Contract>:<field>=<Contract>')}\n\n"
                 f"Example: \n\t{Util.text_blue('Pool:asset=Asset')}\n\n"
                 f"The field {Util.text_blue('asset')} in contract {Util.text_blue('Pool')} is a contract "
                 f"of type {Util.text_blue('Asset')}",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    ADDRESS = CertoraArgument(
        attr_validation_func=Vf.validate_address,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="Sets the address of a contract to a given address",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    STRUCT_LINK = CertoraArgument(
        attr_validation_func=Vf.validate_struct_link,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="Links a slot in a struct with another contract. \n\nFormat: "
                 f"\n\t{Util.text_blue('<Contract>:<slot#>=<Contract>')}\n"
                 f"Example: \n\t{Util.text_blue('Bank:0=BankToken Bank:1=LoanToken')}\n\n"
                 f"The first field in contract {Util.text_blue('Bank')} is a contract "
                 f"of type {Util.text_blue('BankToken')} and the second of type {Util.text_blue('LoanToken')} ",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    PROTOTYPE = CertoraArgument(
        attr_validation_func=Vf.validate_prototype_attr,
        arg_type=AttrUtil.AttrArgType.LIST,
        help_msg="Sets the address of the contract's create code. \n\nFormat: "
                 f"\n\t{Util.text_blue('<hex address>=<Contract>')}\n\n"
                 f"Example: \n\t{Util.text_blue('3d602d80600a3d3981f3363d3d373d3d3d363d73=Foo')}\n\n"
                 f"Contract {Util.text_blue('Foo')} will be created from the code in "
                 f"address {Util.text_blue('3d602d80600a3d3981f3363d3d373d3d3d363d73')}",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    DYNAMIC_BOUND = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        jar_flag='-dynamicCreationBound',
        help_msg="Maximum times a contract will be cloned",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    DYNAMIC_DISPATCH = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-dispatchOnCreated',
        help_msg="Automatically applies the DISPATCHER summary on newly created instances",
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    DEBUG = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        flag='--debug',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    SHOW_DEBUG_TOPICS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        flag='--show_debug_topics',  # added to prevent dup with DEBUG
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    DEBUG_TOPICS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    VERSION = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        help_msg="Shows the tool version",
        argparse_args={
            'action': AttrUtil.VERSION,
            'version': 'This message should never be reached'
        }
    )

    JAR = CertoraArgument(
        attr_validation_func=Vf.validate_jar,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    JAVA_ARGS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        argparse_args={
            'action': AttrUtil.APPEND,
        }
    )

    CHECK_ARGS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        flag='--check_args',  # added to prevent dup with DISABLE_LOCAL_TYPECHECKING
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    BUILD_ONLY = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        flag='--build_only',  # added to prevent dup with CHECK_ARGS
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    BUILD_DIR = CertoraArgument(
        attr_validation_func=Vf.validate_build_dir,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    DISABLE_LOCAL_TYPECHECKING = CertoraArgument(
        flag='--disable_local_typechecking',
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    NO_COMPARE = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        flag='--no_compare',  # added to prevent dup with CHECK_ARGS
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    EXPECTED_FILE = CertoraArgument(
        attr_validation_func=Vf.validate_optional_readable_file,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    QUEUE_WAIT_MINUTES = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        flag='--queue_wait_minutes',  # added to prevent dup with MAX_POLL_MINUTES
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    MAX_POLL_MINUTES = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        flag='--max_poll_minutes',  # added to prevent dup with QUEUE_WAIT_MINUTES
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    LOG_QUERY_FREQUENCY_SECONDS = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        flag='--log_query_frequency_seconds',  # added to prevent dup with QUEUE_WAIT_MINUTES
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    MAX_ATTEMPTS_TO_FETCH_OUTPUT = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        flag='--max_attempts_to_fetch_output',  # added to prevent dup with QUEUE_WAIT_MINUTES
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    DELAY_FETCH_OUTPUT_SECONDS = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        flag='--delay_fetch_output_seconds',  # added to prevent dup with QUEUE_WAIT_MINUTES
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    PROCESS = CertoraArgument(
        argparse_args={
            'action': AttrUtil.UniqueStore,
            'default': 'emv'
        }
    )

    """
    The content of prover_args is added as is to the jar command without any flag. If jar_flag was set to None, this
    attribute would have been skipped altogether. setting jar_flag to empty string ensures that the value will be added
    to the jar as is
    """
    PROVER_ARGS = CertoraArgument(

        arg_type=AttrUtil.AttrArgType.LIST,
        attr_validation_func=validate_prover_args,
        help_msg="Sends flags directly to the prover",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    TYPECHECKER_ARGS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        attr_validation_func=validate_typechecker_args,
        help_msg="Sends flags directly to the typechecker",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    COMMIT_SHA1 = CertoraArgument(
        attr_validation_func=Vf.validate_git_hash,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    DISABLE_AUTO_CACHE_KEY_GEN = CertoraArgument(
        flag='--disable_auto_cache_key_gen',  # added to prevent dup with SKIP_PAYABLE_ENVFREE_CHECK
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    USE_PER_RULE_CACHE = CertoraArgument(
        attr_validation_func=Vf.validate_false,
        jar_flag='-usePerRuleCache',
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore
        }
    )

    UNUSED_SUMMARY_HARD_FAIL = CertoraArgument(
        attr_validation_func=Vf.validate_on_off,
        jar_flag='-unusedSummaryHardFail',
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    MAX_GRAPH_DEPTH = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        jar_flag='-graphDrawLimit',
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    TOOL_OUTPUT = CertoraArgument(
        attr_validation_func=Vf.validate_tool_output_path,
        jar_flag='-json',
        argparse_args={
            'action': AttrUtil.UniqueStore,
        }
    )

    CLOUD_GLOBAL_TIMEOUT = CertoraArgument(
        attr_validation_func=Vf.validate_cloud_global_timeout,
        jar_flag='-globalTimeout',
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    GLOBAL_TIMEOUT = CertoraArgument(
        attr_validation_func=Vf.validate_non_negative_integer,
        jar_flag='-userGlobalTimeout',
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    INTERNAL_FUNCS = CertoraArgument(
        attr_validation_func=Vf.validate_json_file,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    COINBASE_MODE = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_flag='-coinbaseFeaturesMode',
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    CONF_OUTPUT_FILE = CertoraArgument(
        flag='--conf_output_file',
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    GENERATE_MUTATION_CONF = CertoraArgument(
        flag='--generate_mutation_conf',  # added to prevent dup with CONF_OUTPUT_FILE
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    SKIP_PAYABLE_ENVFREE_CHECK = CertoraArgument(
        flag='--skip_payable_envfree_check',  # added to prevent dup with DISABLE_AUTO_CACHE_KEY_GEN
        jar_flag='-skipPayableEnvfreeCheck',
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        jar_no_value=True,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    RUN_SOURCE = CertoraArgument(
        attr_validation_func=Vf.validate_run_source,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    ASSERT_AUTOFINDERS_SUCCESS = CertoraArgument(
        flag="--assert_autofinder_success",
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    CONTRACT_COMPILER_SKIP_SEVERE_WARNING_AS_ERROR = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    PROVER_VERSION = CertoraArgument(
        attr_validation_func=Vf.validate_prover_version,
        help_msg="Instructs the prover to use a tool revision that is not the default",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    SERVER = CertoraArgument(
        attr_validation_func=Vf.validate_server_value,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )
    # resource files are string of the form <label>:<path> the client will add the file to .certora_sources
    # and will change the path from relative/absolute path to
    PROVER_RESOURCE_FILES = CertoraArgument(
        attr_validation_func=Vf.validate_resource_files,
        jar_flag='-resourceFiles',
        arg_type=AttrUtil.AttrArgType.LIST,
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    TEST = CertoraArgument(
        attr_validation_func=Vf.validate_test_value,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    COVERAGE_INFO = CertoraArgument(
        attr_validation_func=Vf.validate_coverage_info,
        jar_flag='-coverageInfo',
        argparse_args={
            'nargs': AttrUtil.SINGLE_OR_NONE_OCCURRENCES,
            'action': AttrUtil.UniqueStore,
            'default': None,  # 'default': when no --coverage_info given
            'const': Vf.CoverageInfoValue.BASIC.name.lower()  # 'default': when empty --coverage_info is given
        }
    )

    FE_VERSION = CertoraArgument(
        attr_validation_func=Vf.validate_fe_value,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    JOB_DEFINITION = CertoraArgument(
        attr_validation_func=Vf.validate_job_definition,
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    MUTATION_TEST_ID = CertoraArgument(
        flag='--mutation_test_id',  # added to prevent dup with CONF_OUTPUT_FILE
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    ALLOW_SOLIDITY_CALLS_IN_QUANTIFIERS = CertoraArgument(
        flag='--allow_solidity_calls_in_quantifiers',
        arg_type=AttrUtil.AttrArgType.BOOLEAN,
        argparse_args={
            'action': AttrUtil.STORE_TRUE
        }
    )

    PARAMETRIC_CONTRACTS = CertoraArgument(
        arg_type=AttrUtil.AttrArgType.LIST,
        attr_validation_func=Vf.validate_contract_name,
        jar_flag='-contract',
        help_msg="Filters the set of contracts whose functions will be used in parametric rules/invariants",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    # something is definitely under-tested here, because I changed this to take
    # a string instead of list of strings and everything just passed!
    ASSERT_CONTRACTS = CertoraArgument(
        attr_validation_func=Vf.validate_assert_contracts,
        arg_type=AttrUtil.AttrArgType.LIST,
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND,
        }
    )

    BYTECODE_JSONS = CertoraArgument(
        attr_validation_func=Vf.validate_json_file,
        arg_type=AttrUtil.AttrArgType.LIST,
        jar_flag='-bytecode',
        help_msg="List of EVM bytecode JSON descriptors",
        argparse_args={
            'nargs': AttrUtil.ONE_OR_MORE_OCCURRENCES,
            'action': AttrUtil.APPEND
        }
    )

    BYTECODE_SPEC = CertoraArgument(
        attr_validation_func=Vf.validate_spec_file,
        jar_flag='-spec',
        help_msg="Spec to use for the provided bytecodes",
        argparse_args={
            'action': AttrUtil.UniqueStore
        }
    )

    def validate_value(self, value: str) -> None:
        if self.value.attr_validation_func is not None:
            try:
                self.value.attr_validation_func(value)
            except Util.CertoraUserInputError as e:
                msg = f'{self.get_flag()}: {e}'
                if isinstance(value, str) and value.strip()[0] == '-':
                    flag_error = f'{value}: Please remember, CLI flags should be preceded with double dashes. ' \
                                 f'{Util.NEW_LINE}For more help run the tool with the option --help'
                    msg = flag_error + msg
                raise Util.CertoraUserInputError(msg) from None

    def get_flag(self) -> str:
        return self.value.flag if self.value.flag is not None else '--' + str(self)

    def get_conf_key(self) -> str:
        dest = self.value.get_dest()
        return dest if dest is not None else self.get_flag().lstrip('--')

    def __str__(self) -> str:
        return self.name.lower()


@lru_cache(maxsize=1, typed=False)
def all_context_keys() -> List[str]:
    return [attr.get_conf_key() for attr in ContextAttribute if attr is not ContextAttribute.CONF_OUTPUT_FILE]


def print_attr_help() -> None:

    table = Table(title="CertoraRun Flags", padding=(1, 1), show_lines=True, header_style="bold orange4")

    table.add_column(Text("Flag", justify="center"), style="cyan", no_wrap=True, width=40)
    table.add_column(Text("Description", justify="center"), style="magenta", width=80)
    table.add_column(Text("Type", justify="center"), style="magenta", justify='center', width=30)

    for attr in ContextAttribute:
        if attr.value.help_msg != '==SUPPRESS==' and attr.get_flag().startswith('--'):
            table.add_row(attr.get_flag(), attr.value.help_msg, str(attr.value.arg_type))

    console = Console()
    console.print(table)
