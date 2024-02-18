"""Get Finetuning Runs API"""
from __future__ import annotations

from concurrent.futures import Future
from typing import Optional, Union, overload

from typing_extensions import Literal

from mcli.api.engine.engine import get_return_response, run_plural_mapi_request
from mcli.api.model.finetune import Finetune
from mcli.api.model.run_event import FormattedRunEvent
from mcli.config import MCLIConfig
from mcli.models.common import ObjectList

QUERY_FUNCTION = 'getFinetuneEvents'
VARIABLE_DATA_NAME = 'getFinetuneEventsData'
# This returns the same data that the create_run function returns
# for consistency when rendering the describe output

QUERY = f"""
query GetFinetuneEvents(${VARIABLE_DATA_NAME}: GetFinetuneEventsInput!) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}) {{
    eventType
    eventTime
    eventMessage
  }}
}}"""


@overload
def list_finetuning_events(
    finetune: Union[str, Finetune],
    *,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> ObjectList[FormattedRunEvent]:
    ...


@overload
def list_finetuning_events(
    finetune: Union[str, Finetune],
    *,
    timeout: Optional[float] = None,
    future: Literal[True] = True,
) -> Future[ObjectList[FormattedRunEvent]]:
    ...


def list_finetuning_events(
    finetune: Union[str, Finetune],
    *,
    timeout: Optional[float] = 10,
    future: bool = False,
):
    """ List finetuning events

    Args:
        finetune (``Optional[str | ``:class:`~mcli.api.model.finetune.Finetune` ``]``):
            A finetune run or finetune run name to delete. Using :class:`~mcli.api.model.finetune.Finetune`
            objects is most efficient. See the note below.
        timeout (``Optional[float]``): Time, in seconds, in which the call should complete.
            If the call takes too long, a :exc:`~concurrent.futures.TimeoutError`
            will be raised. If ``future`` is ``True``, this value will be ignored.
        future (``bool``): Return the output as a :class:`~concurrent.futures.Future`. If True, the
            call to :func:`delete_finetuning_run` will return immediately and the request will
            be processed in the background. This takes precedence over the ``timeout``
            argument. To get the list of :class:`~mcli.api.model.finetune.Finetune` output,
            use ``return_value.result()`` with an optional ``timeout`` argument.
    Returns:
        If future is False:
            A list of :type FormattedRunEvent: objects containing the run event information.
        Otherwise:
            A :class:`~concurrent.futures.Future` that will contain the list of run events
    """

    finetuning_run_name = finetune.name if isinstance(finetune, Finetune) else finetune

    variables = {
        VARIABLE_DATA_NAME: {
            'name': finetuning_run_name,
        },
    }

    cfg = MCLIConfig.load_config()
    cfg.update_entity(variables[VARIABLE_DATA_NAME])

    response = run_plural_mapi_request(
        query=QUERY,
        query_function=QUERY_FUNCTION,
        return_model_type=FormattedRunEvent,
        variables=variables,
    )
    return get_return_response(response, future=future, timeout=timeout)
