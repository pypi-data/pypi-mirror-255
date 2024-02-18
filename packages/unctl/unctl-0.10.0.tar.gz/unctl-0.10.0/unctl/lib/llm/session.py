from .utils import get_llm_instance


class LLMSessionKeeper:

    """
    This class is storing LLM session for failure object
    """

    def __init__(self):
        self._session_id = None
        self.enabled = False

    @property
    def _llm(self):
        return get_llm_instance()

    async def init_session(self, data: list[str] | None = None):
        """
        Initialises LLM session
        """
        if data is None:
            data = []

        self._session_id = await self._llm.initiate_session(data=data)
        self.enabled = True

    async def push_info(self, message: str):
        """
        Requests llm to analyse problem and ask for recommendation

        Args:
            message (str):information or ask to be passed to llm.
        """

        await self._llm.push_info(session_id=self._session_id, data=message)

    async def request_llm_recommendation(
        self,
        message: str | None = None,
        instructions: str | None = None,
        polling_timeout=5,
    ):
        """
        Requests llm to analyse problem and ask for recommendation

        Args:
            message (str | None, optional): additional information or
            ask to be passed to llm. Defaults to None.
        """

        if message is not None:
            await self._llm.push_info(session_id=self._session_id, data=message)

        return await self._llm.get_recommendation(
            self._session_id,
            instructions=instructions,
            polling_timeout=polling_timeout,
        )
