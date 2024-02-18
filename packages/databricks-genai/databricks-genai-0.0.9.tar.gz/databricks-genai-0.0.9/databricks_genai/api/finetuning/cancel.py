"""Cancel a finetuning run"""

from typing import Any, Dict, List, Union

from mcli.api.engine.engine import get_return_response, run_plural_mapi_request
from mcli.config import MCLIConfig

from databricks_genai.api.config import configure_request
from databricks_genai.errors import DatabricksGenAIRequestError
from databricks_genai.types.finetuning import FinetuningRun

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


@configure_request
def cancel(finetuning_runs: Union[str, FinetuningRun, List[str], List[FinetuningRun]]) -> int:
    """Cancel a finetuning run or list of finetuning runs without deleting them
    
    Args:
        finetuning_runs (Union[str, FinetuningRun, List[str], List[FinetuningRun]]): The
            finetuning run(s) to cancel. Can be a single run or a list of runs.
    
    Returns:
        int: The number of finetuning runs cancelled
    """

    if not finetuning_runs:
        raise DatabricksGenAIRequestError('Must provide finetuning run(s) to cancel')

    finetuning_runs_list: List[Union[str, FinetuningRun]] = [finetuning_runs] if isinstance(
        finetuning_runs, (str, FinetuningRun)) else finetuning_runs  # pyright: ignore

    # Extract run names
    finetuning_run_names = [r if isinstance(r, str) else r.name for r in finetuning_runs_list]

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

    try:
        response = run_plural_mapi_request(
            query=QUERY,
            query_function=QUERY_FUNCTION,
            return_model_type=FinetuningRun,
            variables=variables,
        )
        return len(get_return_response(response))
    except Exception as e:
        raise DatabricksGenAIRequestError(
            f'Failed to cancel finetuning run(s) {finetuning_runs}. Please make sure the run '
            'has not completed or failed and try again.') from e
