""" Defines a Run Event """
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from mcli.api.schema.generic_model import DeserializableModel, convert_datetime
from mcli.utils.utils_string_functions import camel_case_to_snake_case


@dataclass()
class FormattedRunEvent(DeserializableModel):
    """ Formatted Run Event """
    event_type: str
    event_time: datetime
    event_message: str

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> FormattedRunEvent:
        """Load the formatted run event from MAPI response.
        """
        args = {camel_case_to_snake_case(key): value for key, value in response.items()}
        return cls(**args)


@dataclass()
class RunEvent(DeserializableModel):
    """ Run Event """
    id: str
    run_id: str
    execution_id: str
    event_type: str
    event_data: Dict[str, Any]
    updated_at: datetime

    @classmethod
    def from_mapi_response(cls, response: Dict[str, Any]) -> RunEvent:
        """Load the run event from MAPI response.
        """
        args = {
            'id': response['id'],
            'run_id': response['runId'],
            'execution_id': response['executionId'],
            'event_type': response['eventType'],
            'event_data': response['eventData'],
            'updated_at': convert_datetime(response['updatedAt']),
        }
        return cls(**args)
