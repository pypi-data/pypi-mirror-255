from abc import ABC, abstractmethod
from unctl.analytics import track_api_error


class LLMAPIError(Exception):
    """LLM API exception class."""

    def __init__(self, message="LLM API error.", identifier=None):
        self.message = f"Returned error API response: {message}"
        super().__init__(self.message)

        track_api_error("APIError", self.message, identifier)


class LLMExceededMessageLengthError(Exception):
    """LLM Exceeded Message Length exception class."""

    def __init__(self, message="LLM Exceeded Message Length error."):
        self.message = f"{message}"
        super().__init__(self.message)


class LanguageModel(ABC):
    @abstractmethod
    async def initiate_session(self, data: list[str] | None = None) -> str:
        """
        This function is used to start LLM session

        Returns:
            str: identifier of LLM context
        """
        pass

    @abstractmethod
    async def push_info(self, session_id: str, data: str):
        """
        Add additional information to session context

        Args:
            session_id (str): identifier of LLM context
            data (str): additional info needed to describe problem
        """
        pass

    @abstractmethod
    async def get_recommendation(
        self, session_id: str, polling_timeout: int, instructions: str | None = None
    ) -> str:
        """
        Requests LLM to get recommendations based on provided information

        Args:
            session_id (str): identifier of LLM context

        Returns:
            str: contains general recommendations based on provided information
        """
        pass
