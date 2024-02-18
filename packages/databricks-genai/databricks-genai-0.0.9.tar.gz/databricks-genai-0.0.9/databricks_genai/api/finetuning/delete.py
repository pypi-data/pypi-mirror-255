"""Delete a finetuning run"""

from typing import Any, Dict, List, Union

from mcli.api.engine.engine import get_return_response, run_plural_mapi_request
from mcli.config import MCLIConfig

from databricks_genai.api.config import configure_request
from databricks_genai.errors import DatabricksGenAIRequestError
from databricks_genai.types.finetuning import FinetuningRun

QUERY_FUNCTION = 'deleteFinetunes'
VARIABLE_DATA_NAME = 'getFinetunesData'
QUERY = f"""
mutation DeleteFinetunes(${VARIABLE_DATA_NAME}: GetFinetunesInput!) {{
  {QUERY_FUNCTION}({VARIABLE_DATA_NAME}: ${VARIABLE_DATA_NAME}) {{
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


@configure_request
def delete(finetuning_runs: Union[str, FinetuningRun, List[str], List[FinetuningRun]]) -> int:
    """Cancel and delete finetuning runs

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
            call to :func:`delete_finetuning_runs` will return immediately and the request will be
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
    if not finetuning_runs:
        raise DatabricksGenAIRequestError('Must provide finetuning run(s) to delete')

    finetuning_runs_list: List[Union[str, FinetuningRun]] = []
    if isinstance(finetuning_runs, (str, FinetuningRun)):
        finetuning_runs_list = [finetuning_runs]
    # Extract run names
    finetuning_run_names = [r.name if isinstance(r, FinetuningRun) else r for r in finetuning_runs_list]

    filters = {}
    if finetuning_run_names:
        filters['name'] = {'in': finetuning_run_names}

    variables: Dict[str, Dict[str, Any]] = {VARIABLE_DATA_NAME: {'filters': filters}}

    cfg = MCLIConfig.load_config()
    cfg.update_entity(variables[VARIABLE_DATA_NAME])

    response = run_plural_mapi_request(
        query=QUERY,
        query_function=QUERY_FUNCTION,
        return_model_type=FinetuningRun,
        variables=variables,
    )
    return len(get_return_response(response))
