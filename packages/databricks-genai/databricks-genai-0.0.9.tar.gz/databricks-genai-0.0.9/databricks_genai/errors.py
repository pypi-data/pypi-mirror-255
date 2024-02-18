"""
Errors for the DatabricksGenAI package.
"""


class DatabricksGenAIError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class DatabricksGenAIRequestError(DatabricksGenAIError):
    """Exception raised for errors in the request.

    Attributes:
        message -- explanation of the error
    """


class DatabricksGenAIResponseError(DatabricksGenAIError):
    """Exception raised for errors in the response.

    Attributes:
        message -- explanation of the error
    """


class DatabricksGenAIConfigError(DatabricksGenAIError):
    """Exception raised for errors in the config.

    Attributes:
        message -- explanation of the error
    """
