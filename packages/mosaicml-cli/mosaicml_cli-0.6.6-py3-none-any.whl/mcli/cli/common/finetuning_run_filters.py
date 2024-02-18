""" Filters for finetuning runs """
import argparse
import fnmatch
from typing import Dict, List, Optional

from mcli.api.exceptions import MCLIException
from mcli.api.finetuning_runs import get_finetuning_runs
from mcli.api.model.finetune import Finetune
from mcli.cli.common.run_filters import _split_glob_filters
from mcli.utils import utils_completers
from mcli.utils.utils_cli import comma_separated
from mcli.utils.utils_model import SubmissionType
from mcli.utils.utils_run_status import RunStatus
from mcli.utils.utils_spinner import console_status


def get_finetuning_runs_with_filters(
    name_filter: Optional[List[str]] = None,
    before_filter: Optional[str] = None,
    after_filter: Optional[str] = None,
    status_filter: Optional[List[RunStatus]] = None,
    latest: bool = False,
    user_filter: Optional[List[str]] = None,
    limit: Optional[int] = None,
    include_details: bool = False,
    action_all: Optional[bool] = None,
) -> List[Finetune]:
    finetuning_runs = []

    if name_filter is None:
        # Accept all that pass other filters
        name_filter = []

    filter_used = any([
        name_filter,
        before_filter,
        after_filter,
        status_filter,
        latest,
        user_filter,
    ])

    if not filter_used:
        if action_all is False:
            raise MCLIException('Must specify at least one filter or --all')

    # Use get_runs only for the non-glob names provided
    glob_filters, run_names = _split_glob_filters(name_filter)

    # If we're getting the latest run, we only need to get one
    if latest:
        limit = 1

    with console_status('Retrieving requested finetuning runs...'):
        filters = {
            'user_emails': user_filter,
            'before': before_filter,
            'after': after_filter,
            'statuses': status_filter,
            'include_details': include_details,
            'limit': limit,
            'timeout': None,
        }
        finetuning_runs = get_finetuning_runs(
            finetuning_runs=(run_names or None) if not glob_filters else None,
            **filters,
        )

    if glob_filters:
        found_runs: Dict[str, Finetune] = {r.name: r for r in finetuning_runs}

        # Any globs will be handled by additional client-side filtering
        filtered = set()
        for pattern in glob_filters:
            for match in fnmatch.filter(found_runs, pattern):
                filtered.add(match)

        expected_names = set(run_names)
        for run_name in found_runs:
            if run_name in expected_names:
                filtered.add(run_name)

        return [found_runs[r] for r in filtered]

    return list(finetuning_runs)


def configure_finetuning_submission_filter_argparser(action: str,
                                                     parser: argparse.ArgumentParser,
                                                     include_all: bool = True) -> argparse.ArgumentParser:
    parser.add_argument(
        dest='name_filter',
        nargs='*',
        metavar='FINETUNE',
        default=None,
        help='String or glob of the name(s) of the runs to get',
    )
    parser.add_argument(
        '--before',
        '-b',
        dest='before_filter',
        help='Filter by finetuning runs that were created before the given timestamp. '
        'Timestamps can be specified in any format that can be parsed by the dateutil library. '
        'For example: --before "2020-01-01 12:00:00"',
    )
    parser.add_argument(
        '--after',
        '-a',
        dest='after_filter',
        help='Filter by finetuning runs that were created after the given timestamp. '
        'Timestamps can be specified in any format that can be parsed by the dateutil library. '
        'For example: --after "2020-01-01 12:00:00"',
    )

    def status(value: str):
        res = comma_separated(value, RunStatus.from_string)
        if res == [RunStatus.UNKNOWN] and value != [RunStatus.UNKNOWN.value]:
            raise TypeError(f'Unknown value {value}')
        return res

    status_parser = parser.add_argument(
        '-s',
        '--status',
        dest='status_filter',
        default=None,
        metavar='STATUS',
        type=status,
        help=f'{action.capitalize()} finetuning runs with the specified statuses (choices: '
        f'{", ".join(SubmissionType.get_status_options(SubmissionType.TRAINING))}). Multiple statuses '
        'should be specified using a comma-separated list, e.g. "failed,pending"',
    )
    status_parser.completer = utils_completers.RunStatusCompleter()  # pyright: ignore
    parser.add_argument(
        '--latest',
        '-l',
        dest='latest',
        action='store_true',
        help='Get only the latest finetuning run',
    )
    parser.add_argument('--user',
                        '-u',
                        dest='user_filter',
                        action='append',
                        help='Filter by user email. Can be specified multiple times. '
                        'For example: --user ')

    if include_all:
        parser.add_argument(
            '--all',
            dest=f'{action}_all',
            action='store_true',
            help=f'{action} all finetuning runs',
        )
    return parser
