"""Implementation of mcli get finetuning-runs, a.k.a. mcli get ft"""
from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generator, List, Optional

from mcli.api.exceptions import MCLIException, cli_error_handler
from mcli.api.model.finetune import Finetune
from mcli.cli.common.finetuning_run_filters import (configure_finetuning_submission_filter_argparser,
                                                    get_finetuning_runs_with_filters)
from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay
from mcli.utils.utils_date import format_timestamp
from mcli.utils.utils_run_status import RunStatus

DEFAULT_DISPLAY_LIMIT = 50

logger = logging.getLogger(__name__)


@dataclass
class FinetuningRunDisplayItem(MCLIDisplayItem):
    """Display item for finetuning runs
    """
    PROGRESS = [
        "□□□□□□□□□□", "■□□□□□□□□□", "■■□□□□□□□□", "■■■□□□□□□□", "■■■■□□□□□□", "■■■■■□□□□□", "■■■■■■□□□□", "■■■■■■■□□□",
        "■■■■■■■■□□", "■■■■■■■■■□", "■■■■■■■■■■"
    ]

    @classmethod
    def _get_run_progress(cls, eta: datetime, start_time: datetime) -> str:
        total_time = (eta - start_time).total_seconds()
        current_time = datetime.now(timezone.utc)
        elapsed_time = (current_time - start_time).total_seconds()
        percentage = min(int((elapsed_time / total_time) * 100), 100)
        return f"{cls.PROGRESS[int(percentage / 10)]}({percentage}%)"

    @classmethod
    def can_calculate_eta(cls, finetuning_run: Finetune) -> bool:
        if not finetuning_run.started_at:
            return False
        if finetuning_run.estimated_end_time and finetuning_run.estimated_end_time > datetime.now(timezone.utc):
            return True
        # default
        return True

    @classmethod
    def from_finetuning_run(cls, finetuning_run: Finetune) -> List[MCLIDisplayItem]:
        run_rows = []
        label = 'End Time'
        eta = '-'
        details = finetuning_run.reason or '-'
        reported_status = finetuning_run.status.display_name
        if details == "Credentials check failed":
            reported_status = 'Failed'
        if finetuning_run.status == RunStatus.RUNNING and finetuning_run.completed_at is None and cls.can_calculate_eta(
                finetuning_run=finetuning_run):
            # Avoid pyright errors
            if not finetuning_run.started_at:
                raise MCLIException("started_at is None")
            label = 'ETA'
            if finetuning_run.estimated_end_time:
                eta = cls._get_run_progress(finetuning_run.estimated_end_time, finetuning_run.started_at)
            # Training is finished, but we shut down the loggers and upload the chkpt
            if '100' in eta:
                details = 'Uploading checkpoint'
        run_rows.append(
            MCLIDisplayItem({
                'name':
                    finetuning_run.name,
                'User':
                    finetuning_run.created_by,
                'Status':
                    reported_status,
                'Details':
                    details,
                'Start Time':
                    format_timestamp(finetuning_run.started_at) if finetuning_run.started_at is not None else '-',
                label:
                    eta if label == 'ETA' else format_timestamp(finetuning_run.completed_at),
            }))
        return run_rows


class MCLIFinetuningRunsDisplay(MCLIGetDisplay):
    """Display manager for finetuning runs
    """

    def __init__(self, models: List[Finetune]):
        self.models = sorted(models, key=lambda x: x.created_at, reverse=True)

    def __iter__(self) -> Generator[MCLIDisplayItem, None, None]:
        for model in self.models:
            items = FinetuningRunDisplayItem.from_finetuning_run(model)
            for item in items:
                yield item


@cli_error_handler('mcli get finetuning-runs')
def cli_get_finetuning_runs(
    name_filter: Optional[List[str]] = None,
    before_filter: Optional[str] = None,
    after_filter: Optional[str] = None,
    status_filter: Optional[List[RunStatus]] = None,
    output: OutputDisplay = OutputDisplay.TABLE,
    latest: bool = False,
    user_filter: Optional[List[str]] = None,
    limit: Optional[int] = DEFAULT_DISPLAY_LIMIT,
    **kwargs,
) -> int:
    """Get a table of ongoing and completed finetuning runs
    """
    del kwargs
    finetuning_runs = get_finetuning_runs_with_filters(name_filter=name_filter,
                                                       before_filter=before_filter,
                                                       after_filter=after_filter,
                                                       status_filter=status_filter,
                                                       latest=latest,
                                                       user_filter=user_filter,
                                                       limit=limit,
                                                       action_all=True)

    display = MCLIFinetuningRunsDisplay(finetuning_runs)
    display.print(output)
    return 0


def get_finetuning_runs_argparser(subparser: argparse._SubParsersAction):
    """Get the argparser for the ``mcli get finetuning-runs`` command
    """
    parser = subparser.add_parser('finetuning-runs',
                                  aliases=['ft'],
                                  help='Get a table of ongoing and completed finetuning runs',
                                  description='Get a table of ongoing and completed finetuning runs',
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.set_defaults(func=cli_get_finetuning_runs)

    def limit(value: str) -> Optional[int]:
        if value.lower() == 'none':
            return None

        return int(value)

    parser.add_argument(
        '--limit',
        help='Maximum number of finetuning runs to return. Finetuning runs will be sorted by creation time. '
        f'Default: {DEFAULT_DISPLAY_LIMIT}',
        default=DEFAULT_DISPLAY_LIMIT,
        type=limit,
    )

    configure_finetuning_submission_filter_argparser('get', parser=parser, include_all=False)
    return parser
