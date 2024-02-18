""" Stop a finetuning run. """
from __future__ import annotations

from concurrent.futures import Future
from typing import Any, Dict, List, Optional, Union, cast, overload

from typing_extensions import Literal

from mcli.api.engine.engine import convert_plural_future_to_singleton, get_return_response, run_plural_mapi_request
from mcli.api.model.finetune import Finetune
from mcli.config import MCLIConfig
from mcli.models.common import ObjectList

__all__ = ['stop_finetuning_runs', 'stop_finetuning_run']

QUERY_FUNCTION = 'stopFinetunes'
VARIABLE_DATA_NAME = 'getFinetunesData'
OPTIONAL_DATA_NAME = 'stopFinetunesData'
QUERY = f"""
mutation StopFinetunes(${VARIABLE_DATA_NAME}: GetFinetunesInput!, ${OPTIONAL_DATA_NAME}: StopFinetunesInput) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}, {OPTIONAL_DATA_NAME}: ${OPTIONAL_DATA_NAME}) {{
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
    isDeleted
  }}
}}"""


@overload
def stop_finetuning_run(
    finetune: Union[str, Finetune],
    *,
    reason: Optional[str] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Finetune:
    ...


@overload
def stop_finetuning_run(
    finetune: Union[str, Finetune],
    *,
    reason: Optional[str] = None,
    timeout: Optional[float] = None,
    future: Literal[True] = True,
) -> Future[Finetune]:
    ...


def stop_finetuning_run(
    finetune: Union[str, Finetune],
    *,
    reason: Optional[str] = None,
    timeout: Optional[float] = 10,
    future: bool = False,
):
    """Stop a finetune

    Stop a run currently running in the MosaicML platform.

    Args:
        finetune (``Optional[str | ``:class:`~mcli.api.model.finetune.Finetune` ``]``):
            A finetune run or finetune run name to stop. Using :class:`~mcli.api.model.finetune.Finetune`
            objects is most efficient. See the note below.
        reason (``Optional[str]``): A reason for stopping the finetune run
        timeout (``Optional[float]``): Time, in seconds, in which the call should complete.
            If the call takes too long, a :exc:`~concurrent.futures.TimeoutError`
            will be raised. If ``future`` is ``True``, this value will be ignored.
        future (``bool``): Return the output as a :class:`~concurrent.futures.Future`. If True, the
            call to :func:`stop_finetuning_run` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the list of :class:`~mcli.api.model.finetune.Finetune` output,
            use ``return_value.result()`` with an optional ``timeout`` argument.

    Raises:
        MAPIException: Raised if stopping the requested runs failed
            A successfully stopped finetune run will have the status ```RunStatus.STOPPED``` # TODO??

    Returns:
        If future is False:
            Stopped :class:`~mcli.api.model.finetune.Finetune` object
        Otherwise:
            A :class:`~concurrent.futures.Future` for the object
    """
    finetuning_runs = cast(Union[List[str], List[Finetune]], [finetune])

    if future:
        res = stop_finetuning_runs(finetuning_runs=finetuning_runs, reason=reason, timeout=None, future=True)
        return convert_plural_future_to_singleton(res)

    return stop_finetuning_runs(finetuning_runs=finetuning_runs, reason=reason, timeout=timeout, future=False)[0]


@overload
def stop_finetuning_runs(
    finetuning_runs: Union[List[str], List[Finetune], ObjectList[Finetune]],
    *,
    reason: Optional[str] = None,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> ObjectList[Finetune]:
    ...


@overload
def stop_finetuning_runs(
    finetuning_runs: Union[List[str], List[Finetune], ObjectList[Finetune]],
    *,
    reason: Optional[str] = None,
    timeout: Optional[float] = None,
    future: Literal[True] = True,
) -> Future[ObjectList[Finetune]]:
    ...


def stop_finetuning_runs(
    finetuning_runs: Union[List[str], List[Finetune], ObjectList[Finetune]],
    *,
    reason: Optional[str] = None,
    timeout: Optional[float] = 10,
    future: bool = False,
):
    """Stop a list of runs TODO

    Stop a list of runs currently running in the MosaicML platform.

    Args:
        runs (``Optional[List[str] | List[``:class:`~mcli.api.model.finetune.Finetune` ``]]``):
            A list of finetuning_runs or finetuning_run names to stop. Using :class:`~mcli.api.model.finetune.Finetune`
            objects is most efficient. See the note below.
        reason (``Optional[str]``): A reason for stopping the finetune run
        timeout (``Optional[float]``): Time, in seconds, in which the call should complete.
            If the call takes too long, a :exc:`~concurrent.futures.TimeoutError`
            will be raised. If ``future`` is ``True``, this value will be ignored.
        future (``bool``): Return the output as a :class:`~concurrent.futures.Future`. If True, the
            call to :func:`stop_finetuning_runs` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the list of :class:`~mcli.api.model.finetune.Finetune` output,
            use ``return_value.result()`` with an optional ``timeout`` argument.

    Raises:
        MAPIException: Raised if stopping any of the requested runs failed. All
            successfully stopped finetuning runs will have the status ```RunStatus.STOPPED```. You can
            freely retry any stopped and unstopped runs if this error is raised due to a
            connection issue.

    Returns:
        If future is False:
            A list of stopped :class:`~mcli.api.model.finetune.Finetune` objects
        Otherwise:
            A :class:`~concurrent.futures.Future` for the list
    """
    # Extract run names
    finetuning_run_names = [r.name if isinstance(r, Finetune) else r for r in finetuning_runs]

    filters = {}
    if finetuning_run_names:
        filters['name'] = {'in': finetuning_run_names}

    variables: Dict[str, Dict[str, Any]] = {VARIABLE_DATA_NAME: {'filters': filters}}

    cfg = MCLIConfig.load_config()
    cfg.update_entity(variables[VARIABLE_DATA_NAME])

    if reason:
        variables[OPTIONAL_DATA_NAME] = {'reason': reason}

    response = run_plural_mapi_request(
        query=QUERY,
        query_function=QUERY_FUNCTION,
        return_model_type=Finetune,
        variables=variables,
    )
    return get_return_response(response, future=future, timeout=timeout)
