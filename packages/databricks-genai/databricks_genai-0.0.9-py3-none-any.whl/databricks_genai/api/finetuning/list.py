"""List multiple finetuning runs"""

from datetime import datetime
from typing import List, Optional, Union

from mcli.api.engine.engine import get_return_response, run_paginated_mapi_request
from mcli.config import MCLIConfig

from databricks_genai.api.config import configure_request
from databricks_genai.types.common import ObjectList
from databricks_genai.types.finetuning import FinetuningRun
from databricks_genai.types.run_status import RunStatus

QUERY_FUNCTION = 'getFinetunesPaginated'
VARIABLE_DATA_NAME = 'getFinetunesPaginatedData'

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

QUERY_WITH_DETAILS_DB = f"""
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


@configure_request
def list(  # pylint: disable=redefined-builtin
    finetuning_runs: Optional[Union[List[str], List[FinetuningRun], ObjectList[FinetuningRun]]] = None,
    *,
    statuses: Optional[Union[List[str], List[RunStatus]]] = None,
    user_emails: Optional[List[str]] = None,
    before: Optional[Union[str, datetime]] = None,
    after: Optional[Union[str, datetime]] = None,
    limit: Optional[int] = None,
):
    """ 
    Internal db get finetuning runs to include dataPrepConfig in details.
    """
    return get_finetuning_runs_paginated(finetuning_runs=finetuning_runs,
                                         statuses=statuses,
                                         user_emails=user_emails,
                                         before=before,
                                         after=after,
                                         limit=limit)


def get_finetuning_runs_paginated(
    finetuning_runs: Optional[Union[List[str], List[FinetuningRun], ObjectList[FinetuningRun]]] = None,
    *,
    statuses: Optional[Union[List[str], List[RunStatus]]] = None,
    user_emails: Optional[List[str]] = None,
    before: Optional[Union[str, datetime]] = None,
    after: Optional[Union[str, datetime]] = None,
    include_details: bool = False,
    limit: Optional[int] = None,
) -> List[FinetuningRun]:
    """List finetuning runs
    
    Args:
        finetuning_runs (Optional[Union[List[str], List[FinetuningRun], ObjectList[FinetuningRun]]], optional): 
        The finetuning runs to list. Defaults to None.
        statuses (Optional[Union[List[str], List[RunStatus]], optional): The statuses to filter by. Defaults to None.
        user_emails (Optional[List[str]], optional): The user emails to filter by. Defaults to None.
        before (Optional[Union[str, datetime]], optional): The date to filter before. Defaults to None.
        after (Optional[Union[str, datetime]], optional): The date to filter after. Defaults to None.
        limit (Optional[int], optional): The maximum number of runs to return. Defaults to None.
    
    Returns:
        ObjectList[FinetuningRun]: A list of finetuning runs
    """
    filters = {}
    if finetuning_runs:
        filters['name'] = {'in': [r.name if isinstance(r, FinetuningRun) else r for r in finetuning_runs]}
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
        query=QUERY_WITH_DETAILS_DB if include_details else QUERY,
        query_function=QUERY_FUNCTION,
        return_model_type=FinetuningRun,
        variables=variables,
    )
    return get_return_response(response)
