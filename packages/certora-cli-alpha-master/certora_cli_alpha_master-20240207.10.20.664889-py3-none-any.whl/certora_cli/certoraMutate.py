#!/usr/bin/env python3

import sys

from pathlib import Path
from typing import List


scripts_dir_path = Path(__file__).parent.resolve()  # containing directory
sys.path.insert(0, str(scripts_dir_path))

from Shared.certoraLogging import LoggingManager
from Shared import certoraUtils as Util

from Mutate import mutateAttribute as Attr
from Mutate import mutateApp as App
from Mutate import mutateValidate as Mv


def mutate_entry_point() -> None:
    run_mutate(sys.argv[1:])


# signature same as run_certora -> second args only for polymorphism
def run_mutate(sys_args: List[str], _: bool = False) -> None:
    logging_manager = LoggingManager()
    if '--debug' in sys_args:
        logging_manager.set_log_level_and_format(debug=True)

    args = Attr.get_args(sys_args)
    mutateApp = App.MutateApp(**args)
    mutateApp.read_conf_file()

    if mutateApp.debug:
        logging_manager.set_log_level_and_format(debug=True)

    if mutateApp.mutation_conf:
        mutateApp.output_dir = App.get_gambit_out_dir(App.load_mutation_conf(mutateApp.mutation_conf))
    else:
        mutateApp.output_dir = None

    validator = Mv.MutateValidator(mutateApp)
    validator.validate()
    mutateApp.validate_args()

    if mutateApp.test == str(Util.TestValue.CHECK_ARGS):
        raise Util.TestResultsReady(mutateApp)

    # default mode is async. That is, we both _submit_ and _collect_
    if mutateApp.sync:
        App.check_key_exists()
        # sync mode means we submit, then we poll for the specified amount of minutes
        # todo - to validate vvvv
        if not mutateApp.prover_conf and not mutateApp.orig_run:
            # sync mode means we submit + collect. If the user just wants to collect, do not add --sync
            raise Util.CertoraUserInputError("Must provide a conf file in sync mode. If you wish to poll on a "
                                             "previous submission, omit `--sync`.")
        mutateApp.submit()
        mutateApp.poll_collect()
    else:
        # if the user did not supply a conf file or a link to an original run,
        # we will check whether there is a collect file and poll it
        # todo vvvv
        if not mutateApp.prover_conf and not mutateApp.orig_run:
            assert mutateApp.collect_file, \
                "You must use either a prover configuration file, a collect file, or an original run link"
            ready = mutateApp.collect()
            if not ready:
                raise Util.CertoraUserInputError("The report might broken because some "
                                                 "results could not be fetched. "
                                                 f"Check the {mutateApp.collect_file} file to investigate.")
        else:
            App.check_key_exists()
            mutateApp.submit()


if __name__ == '__main__':
    mutate_entry_point()
