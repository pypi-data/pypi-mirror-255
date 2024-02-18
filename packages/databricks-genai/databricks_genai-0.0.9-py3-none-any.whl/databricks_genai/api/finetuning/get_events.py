"""List events for a finetuning run"""

from typing import List, Union

from mcli.api.engine.engine import get_return_response, run_plural_mapi_request
from mcli.config import MCLIConfig

from databricks_genai.api.config import configure_request
from databricks_genai.types.finetuning import FinetuningEvent, FinetuningRun

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


@configure_request
def get_events(finetuning_run: Union[str, FinetuningRun]) -> List[FinetuningEvent]:
    """List finetuning runs
    
    Args:
        finetuning_run (Union[str, FinetuningRun]): The finetuning run to get events for.

    Returns:
        List[FinetuningEvent]: A list of finetuning events. Each event has an event 
            type, time, and message.
    """
    finetuning_run_name = finetuning_run.name if isinstance(finetuning_run, FinetuningRun) else finetuning_run

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
        return_model_type=FinetuningEvent,
        variables=variables,
    )
    return get_return_response(response)
