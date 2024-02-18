"""Implementation of mcli describe finetuning-run"""
from __future__ import annotations

import logging
from typing import Dict, Generator, List, Optional, TypeVar

from dateutil.parser import parse
from rich.markup import escape
from rich.table import Table

from mcli.api.exceptions import cli_error_handler
from mcli.api.model.finetune import Finetune
from mcli.api.model.run_event import FormattedRunEvent
from mcli.cli.common.finetuning_run_filters import get_finetuning_runs_with_filters
from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay, create_vertical_display_table
from mcli.utils.utils_date import format_timestamp
from mcli.utils.utils_logging import FormatString, console, format_string

logger = logging.getLogger(__name__)


# Displays
class MCLIDescribeFinetuningRunDisplay(MCLIGetDisplay):
    """ Vertical table view of run details """

    def __init__(self, models: List[Finetune]):
        self.models = sorted(models, key=lambda x: x.created_at, reverse=True)
        self.include_reason_in_display = any(m.reason for m in models)

    @property
    def index_label(self) -> str:
        return ""

    def create_custom_table(self, data: List[Dict[str, str]]) -> Optional[Table]:
        if not self.include_reason_in_display:
            del data[0]['Details']
        return create_vertical_display_table(data=data[0])

    def __iter__(self) -> Generator[MCLIDisplayItem, None, None]:
        for model in self.models:
            reported_status = model.status.display_name
            if model.events and any(event.event_type == "CHECK_FAILED" for event in model.events):
                reported_status = 'Failed'
            display_config = {
                'Run Name': model.name,
                'User': model.created_by,
                'Status': reported_status,
                'Details': model.reason,
            }
            if model.estimated_end_time:
                display_config['Estimated end time'] = format_timestamp(model.estimated_end_time)

            item = MCLIDisplayItem(display_config)
            yield item


def format_event_log(run_events: List[FormattedRunEvent]) -> Table:
    grid = Table(title='Event Log', expand=False, padding=(0, 2, 0, 2))
    grid.add_column(header='Time', justify='left')
    grid.add_column(header='Event', justify='left')

    for event in run_events:
        text = event.event_message
        if len(text) > 0:
            if isinstance(event.event_time, str):
                event_time = parse(event.event_time)
            else:
                event_time = event.event_time
            grid.add_row(format_timestamp(event_time), escape(text))
    return grid


def format_status(status: str) -> str:
    status = status.lower().capitalize()

    if status == 'Failed':
        return f'[red]{status}[/]'

    if status == 'Stopped':
        return f'[bright_black]{status}[/]'

    return status


T = TypeVar('T')


@cli_error_handler("mcli describe finetuning-run")
def describe_finetuning_run(
    finetuning_run_name: Optional[str],
    output: OutputDisplay = OutputDisplay.TABLE,
    **kwargs,
):
    """
    Fetches details of a finetuning run
    """
    del kwargs

    latest = not finetuning_run_name
    name_filter = [finetuning_run_name] if finetuning_run_name else []

    finetuning_runs = get_finetuning_runs_with_filters(name_filter=name_filter, latest=latest, include_details=True)

    if len(finetuning_runs) == 0:
        print(f'No finetuning runs found with name: {finetuning_run_name}')
        return
    finetune = finetuning_runs[0]

    # Finetuning run details section
    print(format_string('Run Details', FormatString.BOLD))
    details_display = MCLIDescribeFinetuningRunDisplay([finetune])
    details_display.print(output)
    print()

    # Finetuning run event log section
    finetune_events = finetune.events
    if finetune_events:
        console.print(format_event_log(finetune_events))
        print()

    # Finetuning experiment tracker
    # print(format_string('Experiment Tracker', FormatString.BOLD))
    # TODO: add experiment tracker links

    # Finetuning run config
    if finetune.submitted_config:
        print(format_string('Submitted Finetuning Run Configuration', FormatString.BOLD))
        print(finetune.submitted_config.to_yaml())
