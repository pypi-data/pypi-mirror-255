"""Finetuned model object"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple

from mcli.api.exceptions import MAPIException
from mcli.api.model.run_event import FormattedRunEvent
from mcli.api.schema.generic_model import DeserializableModel, convert_datetime
from mcli.models.finetune_config import FinetuneConfig
from mcli.utils.utils_run_status import RunStatus


# TODO: maybe rename to FinetuningRun for consistency, but honestly I like Finetune better
@dataclass
class Finetune(DeserializableModel):
    """A Finetune that has been run on the MosaicML platform
    
    Args:
        id: The unique identifier for this finetuning run.
        name: The name of the finetuning run.
        status: The current status of the finetuning run. This is a RunStatus enum, which has values
            such as ``PENDING``, ``RUNNING``, or ``COMPLETED``.
        created_at: The timestamp at which the finetuning run was created.
        updated_at: The timestamp at which the finetuning run was last updated.
        created_by: The email address of the user who created the finetuning run.
        started_at: The timestamp at which the finetuning run was started.
        completed_at: The timestamp at which the finetuning run was completed.
        reason: The reason for the finetuning run's current status, such as ``Run completed successfully``.
    """
    id: str
    name: str
    status: RunStatus
    created_at: datetime
    updated_at: datetime
    created_by: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    reason: Optional[str] = None
    estimated_end_time: Optional[datetime] = None
    # TODO: add task type here

    # Finetuning Run config - user inputs
    model: Optional[str] = None
    save_folder: Optional[str] = None
    train_data_path: Optional[str] = None

    # Details
    submitted_config: Optional[FinetuneConfig] = None
    events: Optional[List[FormattedRunEvent]] = None

    _required_properties: Tuple[str] = tuple([
        'id',
        'name',
        'status',
        'createdByEmail',
        'createdAt',
        'updatedAt',
    ])

    # TODO: implement stop and delete functions on this model

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> Finetune:
        missing = set(cls._required_properties) - set(response)
        if missing:
            raise MAPIException(
                status=HTTPStatus.BAD_REQUEST,
                message=f'Missing required key(s) in response to deserialize Finetune object: {", ".join(missing)}',
            )
        started_at = convert_datetime(response['startedAt']) if response.get('startedAt', None) else None
        completed_at = convert_datetime(response['completedAt']) if response.get('completedAt', None) else None
        estimated_end_time = convert_datetime(response['estimatedEndTime']) if response.get('estimatedEndTime',
                                                                                            None) else None

        args = {
            'id': response['id'],
            'name': response['name'],
            'created_at': convert_datetime(response['createdAt']),
            'updated_at': convert_datetime(response['updatedAt']),
            'started_at': started_at,
            'completed_at': completed_at,
            'status': RunStatus.from_string(response['status']),
            'reason': response.get('reason', ''),
            'created_by': response['createdByEmail'],
            'estimated_end_time': estimated_end_time,
        }

        details = response.get('details', {})
        if details:
            args['model'] = details.get('model')
            args['save_folder'] = details.get('saveFolder')
            args['train_data_path'] = details.get('trainDataPath')

            config_copy = deepcopy(details)
            # Remove events from details to keep only config properties
            if "formattedFinetuningEvents" in config_copy:
                del config_copy["formattedFinetuningEvents"]

            args['submitted_config'] = FinetuneConfig.from_mapi_response(config_copy)

            formatted_finetuning_events = [
                FormattedRunEvent.from_mapi_response(event) for event in details.get('formattedFinetuningEvents', [])
            ]
            args['events'] = sorted(formatted_finetuning_events, key=lambda x: x.event_time)

        return cls(**args)
