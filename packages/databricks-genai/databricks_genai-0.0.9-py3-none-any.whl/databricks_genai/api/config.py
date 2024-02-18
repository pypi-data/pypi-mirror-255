"""Wrapper around MAPI engine in MCLI."""

import logging
import os
from typing import Any, Callable, Tuple, TypeVar

from databricks.sdk import WorkspaceClient
from mcli import MAPIException, config
from mcli.api.exceptions import MultiMAPIException

from databricks_genai import errors

_TCallable = TypeVar('_TCallable', bound=Callable[..., Any])  # pylint: disable=invalid-name

logger = logging.getLogger(__name__)

GENAI_LOCAL_ENV = 'GENAI_LOCAL'


def get_me() -> str:
    """
    Get who is currently logged in.

    Returns:
        str: The name of the current user.
    """

    if os.environ.get(GENAI_LOCAL_ENV, '').lower() == 'true':
        return 'me'

    w = WorkspaceClient()
    me = w.current_user.me().user_name
    logger.debug(f'You are {me}')
    return me


def get_config_from_env() -> Tuple[str, str]:
    """
    Get api key and endpoint from the current MAPI environment.

    Returns:
        Tuple[str, str]: The API key and endpoint.
    """
    if os.environ.get(GENAI_LOCAL_ENV, '').lower() == 'true':
        return 'local', 'local'

    w = WorkspaceClient()
    ctx = w.dbutils.entry_point.getDbutils().notebook().getContext()
    api_url = ctx.apiUrl().get()
    api_token = ctx.apiToken().get()
    return api_token, f'{api_url}/api/2.0/genai-mapi/graphql'


def configure_request(func: _TCallable) -> _TCallable:
    """
    Decorator that configures a default retry policy for all MAPI requests

    Args:
        func (Callable[..., Any]): The function that should be retried
    """

    def setup(*args, **kwargs):
        api_token, endpoint = get_config_from_env()

        previous_api_key = os.getenv(config.MOSAICML_API_KEY_ENV)
        previous_endpoint = os.getenv(config.MOSAICML_API_ENDPOINT_ENV)

        logger.debug(f"Setting up MAPI connection with api_token {api_token} and endpoint {endpoint}")

        if os.environ.get('GENAI_LOCAL', '').lower() != 'true':
            os.environ[config.MOSAICML_API_KEY_ENV] = f'Bearer {api_token}'
            os.environ[config.MOSAICML_API_ENDPOINT_ENV] = endpoint

        try:
            res = func(*args, **kwargs)
        except TimeoutError as e:
            raise errors.DatabricksGenAIRequestError(f'Timeout connecting to {endpoint}') from e
        except MAPIException as e:
            if isinstance(e, MultiMAPIException):
                e = e.errors[0]
            raise errors.DatabricksGenAIRequestError(e.message)

        if previous_api_key:
            os.environ[config.MOSAICML_API_KEY_ENV] = previous_api_key
        if previous_endpoint:
            os.environ[config.MOSAICML_API_ENDPOINT_ENV] = previous_endpoint

        return res

    return setup  # pyright: ignore
