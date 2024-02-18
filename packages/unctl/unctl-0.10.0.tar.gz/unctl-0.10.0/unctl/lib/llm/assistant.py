import os
import asyncio
import tiktoken
import openai
from openai import OpenAI, APIError
import backoff
from openai.types.beta import Assistant
from openai.types.beta.thread_create_params import Message
from openai._types import NOT_GIVEN, NotGiven

from unctl.lib.llm.instructions import ASSISTANT, ASSISTANTS, INSTRUCTIONS

from .base import LLMExceededMessageLengthError, LanguageModel, LLMAPIError

POLL_MAX_COUNT = 20

# From https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo
MAX_TOKEN_COUNT = 8192


class OpenAIAssistant(LanguageModel):
    _assistant_name = ""
    _instance = None
    _client: OpenAI
    _assistant: Assistant
    _model: str = "gpt-4"
    _provider: str

    def __new__(cls, *args, **kwargs):
        # Create a new instance only if it doesn't exist
        if cls._instance is None:
            cls._instance = super(OpenAIAssistant, cls).__new__(cls)
        return cls._instance

    def __init__(self, provider):
        super().__init__()

        self._provider = provider
        self._assistant_name = ASSISTANTS[self._provider]

        if os.getenv("OPENAI_API_KEY") is None:
            raise Exception("OPENAI_API_KEY is not set")

        openai.api_key = os.getenv("OPENAI_API_KEY")

        # override default model
        model = os.getenv("OPENAI_MODEL")
        if model is not None:
            self._model = model

        # async client getting stuck on some operations because of beta
        # requests are relatively fast so can use sync client so far
        self._client = OpenAI()

        self._assistant = self._get_assistant()

    def _get_assistant(self):
        has_next_page = True
        last_assistant_id = NOT_GIVEN
        while has_next_page:
            results = self._list_assistants(after=last_assistant_id)

            if results.data is not None:
                for assistant in results.data:
                    same_name = assistant.name == self._assistant_name
                    same_model = assistant.model == self._model
                    if same_name and same_model:
                        return assistant
            else:
                break

            has_next_page = results.has_next_page()
            if len(results.data) > 0:
                last_assistant_id = results.data[-1].id

            if not has_next_page:
                break

        # create assistant if it doesn't exist
        print(f"Assistant {self._assistant_name} not found. Creating one...")
        return self._create_assistant()

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    def _list_assistants(self, after: str | NotGiven = NOT_GIVEN):
        return self._client.beta.assistants.list(after=after)

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    def _create_assistant(self):
        return self._client.beta.assistants.create(
            name=self._assistant_name,
            model=self._model,
            instructions=INSTRUCTIONS[self._provider][ASSISTANT],
        )

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    async def _start_thread(self, messages: list[Message]):
        return self._client.beta.threads.create(messages=messages)

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    async def _append_message(self, thread_id: str, content: str):
        return self._client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=content
        )

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    async def _run_thread(
        self, thread_id: str, instructions: str | NotGiven = NOT_GIVEN
    ):
        return self._client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self._assistant.id,
            instructions=instructions,
        )

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    async def _fetch_run(self, thread_id: str, run_id: str):
        return self._client.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run_id
        )

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    async def _fetch_thread(self, thread_id: str):
        return self._client.beta.threads.messages.list(
            thread_id=thread_id, order="desc"
        )

    async def initiate_session(self, data: list[str] | None = None):
        if data is None:
            data = []

        messages = [Message(role="user", content=content) for content in data]
        try:
            thread = await self._start_thread(messages=messages)
            return thread.id
        except APIError as e:
            raise LLMAPIError(f"{e.message}")

    async def push_info(self, session_id: str, data: str):
        # check tokens for the data
        enc = tiktoken.encoding_for_model(self._model)
        tokens = enc.encode(data)
        if len(tokens) > MAX_TOKEN_COUNT:
            raise LLMExceededMessageLengthError()

        try:
            await self._append_message(thread_id=session_id, content=data)
        except APIError as e:
            raise LLMAPIError(f"{e.message}")

    async def get_recommendation(
        self, session_id: str, polling_timeout: int, instructions: str | None = None
    ):
        if instructions is None:
            instructions = NOT_GIVEN

        try:
            run = await self._run_thread(
                thread_id=session_id, instructions=instructions
            )

            poll_count = 0
            while run.status not in ["cancelled", "failed", "completed", "expired"]:
                await asyncio.sleep(polling_timeout * (poll_count + 1))
                run = await self._fetch_run(thread_id=session_id, run_id=run.id)
                poll_count = poll_count + 1

                if poll_count >= POLL_MAX_COUNT:
                    raise LLMAPIError("Thread run exceeded threshold")

            if run.status == "completed":
                thread = await self._fetch_thread(thread_id=session_id)
                if len(thread.data) > 0:
                    last_response = thread.data[0].content
                    if len(last_response) > 0:
                        recommendation = last_response[0]
                        return recommendation.text.value

            return f"Thread run finished with status {run.status}"
        except APIError as e:
            raise LLMAPIError(f"{e.message}")
