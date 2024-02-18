"""Get Finetuning Runs API"""
from __future__ import annotations

from concurrent.futures import Future
from datetime import datetime
from typing import List, Optional, Union, overload

from typing_extensions import Literal

from mcli.api.engine.engine import get_return_response, run_paginated_mapi_request
from mcli.api.model.finetune import Finetune
from mcli.config import MCLIConfig
from mcli.models.common import ObjectList
from mcli.utils.utils_run_status import RunStatus

QUERY_FUNCTION = 'getFinetunesPaginated'
VARIABLE_DATA_NAME = 'getFinetunesPaginatedData'
# This returns the same data that the create_run function returns
# for consistency when rendering the describe output
QUERY = f"""
query GetFinetunesPaginated(${VARIABLE_DATA_NAME}: GetFinetunesPaginatedInput!) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}) {{
    cursor
    hasNextPage
    finetunes {{
        id
        name
        status
        createdById
        createdByEmail
        createdAt
        updatedAt
        startedAt
        completedAt
        reason
        estimatedEndTime
        isDeleted
    }}
  }}
}}"""

QUERY_WITH_DETAILS = f"""
query GetFinetunesPaginated(${VARIABLE_DATA_NAME}: GetFinetunesPaginatedInput!) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}) {{
    cursor
    hasNextPage
    finetunes {{
        id
        name
        status
        createdById
        createdByEmail
        createdAt
        updatedAt
        startedAt
        completedAt
        reason
        estimatedEndTime
        isDeleted
        details {{
            model
            taskType
            trainDataPath
            saveFolder
            evalDataPath
            evalPrompts
            trainingDuration
            learningRate
            contextLength
            experimentTracker
            customWeightsPath
            formattedFinetuningEvents {{
                eventType
                eventTime
                eventMessage    
            }}
        }}
    }}
  }}
}}"""
"""
Same query as above, but with dataPrepConfig included in details, which only
pertains to databricks users.
"""
_QUERY_WITH_DETAILS_DB = f"""
query GetFinetunesPaginated(${VARIABLE_DATA_NAME}: GetFinetunesPaginatedInput!) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}) {{
    cursor
    hasNextPage
    finetunes {{
        id
        name
        status
        createdById
        createdByEmail
        createdAt
        updatedAt
        startedAt
        completedAt
        reason
        estimatedEndTime
        isDeleted
        details {{
            model
            taskType
            trainDataPath
            saveFolder
            evalDataPath
            evalPrompts
            trainingDuration
            learningRate
            contextLength
            experimentTracker
            customWeightsPath
            dataPrepConfig
            formattedFinetuningEvents {{
                eventType
                eventTime
                eventMessage    
            }}
        }}
    }}
  }}
}}"""


@overload
def get_finetuning_runs(
    finetuning_runs: Optional[Union[List[str], List[Finetune], ObjectList[Finetune]]] = None,
    *,
    statuses: Optional[Union[List[str], List[RunStatus]]] = None,
    user_emails: Optional[List[str]] = None,
    before: Optional[Union[str, datetime]] = None,
    after: Optional[Union[str, datetime]] = None,
    include_details: bool = False,
    limit: Optional[int] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> ObjectList[Finetune]:
    ...


@overload
def get_finetuning_runs(
    finetuning_runs: Optional[Union[List[str], List[Finetune], ObjectList[Finetune]]] = None,
    *,
    statuses: Optional[Union[List[str], List[RunStatus]]] = None,
    user_emails: Optional[List[str]] = None,
    before: Optional[Union[str, datetime]] = None,
    after: Optional[Union[str, datetime]] = None,
    include_details: bool = False,
    limit: Optional[int] = None,
    timeout: Optional[float] = None,
    future: Literal[True] = True,
) -> Future[ObjectList[Finetune]]:
    ...


def get_finetuning_runs(
    finetuning_runs: Optional[Union[List[str], List[Finetune], ObjectList[Finetune]]] = None,
    *,
    statuses: Optional[Union[List[str], List[RunStatus]]] = None,
    user_emails: Optional[List[str]] = None,
    before: Optional[Union[str, datetime]] = None,
    after: Optional[Union[str, datetime]] = None,
    include_details: bool = False,
    limit: Optional[int] = None,
    timeout: Optional[float] = 10,
    future: bool = False,
):
    """ Get finetuning runs

    Args:
        finetuning_runs: A list of finetuning run names or :type Finetune: objects.
        statuses: A list of :type RunStatus: objects or strings.
        user_emails: A list of user emails.
        before: Filter for finetuning runs before a datetime or string representing a datetime.
        after: Filter for finetuning runs after datetime or string representing a datetime.
        include_details: Include finetuning run details.
        limit: Limit the number of finetuning runs returned.
        timeout: Timeout for the request.
        future: Whether to return a :type Future: object or not.
    Returns:
        A list of :type Finetune: objects containing the finetuning runs' information.
    """
    filters = {}
    if finetuning_runs:
        filters['name'] = {'in': [r.name if isinstance(r, Finetune) else r for r in finetuning_runs]}
    if statuses:
        filters['status'] = {'in': [s.value if isinstance(s, RunStatus) else s for s in statuses]}
    if before or after:
        date_filters = {}
        if before:
            date_filters['lt'] = before.astimezone().isoformat() if isinstance(before, datetime) else before
        if after:
            date_filters['gte'] = after.astimezone().isoformat() if isinstance(after, datetime) else after
        filters['createdAt'] = date_filters

    variables = {
        VARIABLE_DATA_NAME: {
            'filters': filters,
            'includeDeleted': False,
            'limit': limit,
        },
    }

    cfg = MCLIConfig.load_config()
    cfg.update_entity(variables[VARIABLE_DATA_NAME])
    if user_emails:
        if variables[VARIABLE_DATA_NAME].get('entity'):
            variables[VARIABLE_DATA_NAME]['entity']['emails'] = user_emails
        else:
            variables[VARIABLE_DATA_NAME]['entity'] = {'emails': user_emails}

    response = run_paginated_mapi_request(
        query=QUERY if not include_details else QUERY_WITH_DETAILS,
        query_function=QUERY_FUNCTION,
        return_model_type=Finetune,
        variables=variables,
    )
    return get_return_response(response, future=future, timeout=timeout)


def _db_get_finetuning_runs(
    finetuning_runs: Optional[Union[List[str], List[Finetune], ObjectList[Finetune]]] = None,
    *,
    statuses: Optional[Union[List[str], List[RunStatus]]] = None,
    user_emails: Optional[List[str]] = None,
    before: Optional[Union[str, datetime]] = None,
    after: Optional[Union[str, datetime]] = None,
    include_details: bool = False,
    limit: Optional[int] = None,
    timeout: Optional[float] = 10,
    future: bool = False,
):
    """ 
    Internal db get finetuning runs to include dataPrepConfig in details.
    TODO: delete this function once this finetuning moves to a different SDK.
    """
    filters = {}
    if finetuning_runs:
        filters['name'] = {'in': [r.name if isinstance(r, Finetune) else r for r in finetuning_runs]}
    if statuses:
        filters['status'] = {'in': [s.value if isinstance(s, RunStatus) else s for s in statuses]}
    if before or after:
        date_filters = {}
        if before:
            date_filters['lt'] = before.astimezone().isoformat() if isinstance(before, datetime) else before
        if after:
            date_filters['gte'] = after.astimezone().isoformat() if isinstance(after, datetime) else after
        filters['createdAt'] = date_filters

    variables = {
        VARIABLE_DATA_NAME: {
            'filters': filters,
            'includeDeleted': False,
            'limit': limit,
        },
    }

    cfg = MCLIConfig.load_config()
    cfg.update_entity(variables[VARIABLE_DATA_NAME])
    if user_emails:
        if variables[VARIABLE_DATA_NAME].get('entity'):
            variables[VARIABLE_DATA_NAME]['entity']['emails'] = user_emails
        else:
            variables[VARIABLE_DATA_NAME]['entity'] = {'emails': user_emails}

    response = run_paginated_mapi_request(
        query=QUERY if not include_details else _QUERY_WITH_DETAILS_DB,
        query_function=QUERY_FUNCTION,
        return_model_type=Finetune,
        variables=variables,
    )
    return get_return_response(response, future=future, timeout=timeout)
