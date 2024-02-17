import logging
from typing import Any, Dict, List, Union, cast, Callable, Optional

from ..types import (
    CallbackManager, Callbacks, ChatMessages, create_base_retry_decorator,
    ProviderBase, BaseMessage, Message, ManipulationManager, EmbeddingsData,
    Manipulations, GoogleGenAIInput, completion_decorator, chat_decorator,
    ChatData, CompletionData, HumanMessage, AIMessage, SystemMessage, embeddings_decorator
)
from ..utils import logger

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class GenAIError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(
            self.message
        )


def _create_retry_decorator() -> Callable[[Any], Any]:
    """Returns a tenacity retry decorator, preconfigured to handle PaLM exceptions"""
    import google.api_core.exceptions

    multiplier = 2
    min_seconds = 1
    max_seconds = 60
    max_retries = 5

    return retry(
        reraise=True,
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=multiplier,
                              min=min_seconds, max=max_seconds),
        retry=(
            retry_if_exception_type(
                google.api_core.exceptions.ResourceExhausted)
            | retry_if_exception_type(google.api_core.exceptions.ServiceUnavailable)
            | retry_if_exception_type(google.api_core.exceptions.GoogleAPIError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )


def _response_to_result(
    response: Any,
):

    if not response.candidates:
        raise GenAIError("401",
                         "ChatResponse must have at least one candidate.")

    generations: List[BaseMessage] = []
    for candidate in response.candidates:
        author = candidate.get("author")
        if author is None:
            raise GenAIError("401",
                             f"ChatResponse must have an author: {candidate}")

        content = candidate.get("content", "")
        if content is None:
            raise GenAIError("401",
                             f"ChatResponse must have a content: {candidate}")

        if author == "human":
            generations.append(
                HumanMessage(content=content),
            )
        else:
            generations.append(
                AIMessage(content=content),
            )

    return generations


def _messages_to_prompt_dict(
    input_messages: List[BaseMessage],
):
    import google.generativeai as genai

    context: str = ""
    examples: List[genai.types.MessageDict] = []
    messages: List[genai.types.MessageDict] = []

    remaining = list(enumerate(input_messages))

    while remaining:
        index, input_message = remaining.pop(0)

        if isinstance(input_message, SystemMessage):
            if index != 0:
                raise GenAIError("401",
                                 "System message must be first input message.")
            context = cast(str, input_message.content)
        elif isinstance(input_message, AIMessage):
            messages.append(
                genai.types.MessageDict(
                    author="ai", content=input_message.content)
            )
        elif isinstance(input_message, HumanMessage):
            messages.append(
                genai.types.MessageDict(
                    author="human", content=input_message.content)
            )
        elif isinstance(input_message, BaseMessage):
            messages.append(
                genai.types.MessageDict(
                    author=input_message.role, content=input_message.content
                )
            )
        else:
            raise GenAIError("401",
                             "Messages without an explicit role not supported by PaLM API."
                             )

    return genai.types.MessagePromptDict(
        context=context,
        examples=examples,
        messages=messages,
    )


def _strip_erroneous_leading_spaces(text: str) -> str:
    """Strip erroneous leading spaces from text.

    The PaLM API will sometimes erroneously return a single leading space in all
    lines > 1. This function strips that space.
    """
    has_leading_space = all(
        not line or line[0] == " " for line in text.split("\n")[1:])
    if has_leading_space:
        return text.replace("\n ", "\n")
    else:
        return text


class GoogleGenAIProvider(ProviderBase):

    def __init__(self, configs: GoogleGenAIInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate(api_key=configs.api_key)
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: GoogleGenAIInput = configs

    @classmethod
    def model_validate(cls, api_key):
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Could not import google.generativeai python package. "
                "Please install it with `pip install google-generativeai`"
            )

    @completion_decorator
    def completion(
        self,
        prompt: Message,
        data: Optional[CompletionData] = None,
        configs: Optional[GoogleGenAIInput] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ) -> CompletionData:
        try:
            if data is None:
                raise Exception("Decorator didnt Initialized Data")
            data = self.chat_with_retry(data, callbacks)
            return data
        except Exception as e:
            raise e

    @chat_decorator
    def chat(
        self,
        messages: ChatMessages,
        data: Optional[ChatData] = None,
        configs: Optional[GoogleGenAIInput] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ) -> ChatData:
        try:
            if data is None:
                raise Exception("Decorator didnt Initialized Data")
            data = self.chat_with_retry(data, callbacks)
            return data
        except Exception as e:
            raise e

    def chat_with_retry(self, data: Union[CompletionData, ChatData], callbacks) -> Any:
        """Use tenacity to retry the completion call."""
        retry_decorator = _create_retry_decorator()

        @retry_decorator
        def _chat_with_retry(data: Union[CompletionData, ChatData], callbacks) -> Any:
            return self.generate(data, callbacks)

        return _chat_with_retry(data, callbacks)

    def generate(self, data: Union[CompletionData, ChatData], callbacks):
        try:
            import google.generativeai as genai

            if isinstance(data, ChatData):

                prompt = _messages_to_prompt_dict(data.messages)

                response: genai.types.ChatResponse = genai.chat(
                    prompt=prompt,
                    model=data.configs.provider_model,
                    top_k=data.configs.top_k,
                    top_p=data.configs.top_p,
                    temperature=data.configs.temperature,
                    # candidate_count=data.configs.n,
                )
                generations = _response_to_result(response)
                data = self.data_to_response(
                    data,
                    generations[-1].content,
                    model=response.model,
                )

            else:
                completion = genai.generate_text(
                    prompt=data.prompt.content,
                    model=data.configs.provider_model,
                    top_k=data.configs.top_k,
                    top_p=data.configs.top_p,
                    temperature=data.configs.temperature,
                    # candidate_count=data.configs.n,
                )

                generations = []
                for candidate in completion.candidates:
                    raw_text = candidate["output"]
                    stripped_text = _strip_erroneous_leading_spaces(raw_text)
                    generations.append(AIMessage(content=stripped_text))
                data = self.data_to_response(
                    data,
                    generations[-1].content
                )

            return data
        except Exception as e:
            raise e

    @embeddings_decorator
    def embedding(
        self,
        texts: List[str],
        data: Optional[EmbeddingsData] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ) -> EmbeddingsData:
        try:
            if data is None:
                raise Exception("Decorator didnt Initialized Data")
            data = self.embed_with_retry(data, callbacks)
            return data
        except Exception as e:
            raise e

    def embed_with_retry(self, data: EmbeddingsData, callbacks):
        import google.api_core.exceptions

        retry_decorator = create_base_retry_decorator(
            [google.api_core.exceptions.ResourceExhausted, google.api_core.exceptions.Aborted, google.api_core.exceptions.GoogleAPIError], max_retries=data.configs.max_retries, run_manager=self.callback_manager)

        @retry_decorator
        def _embed_with_retry(data: EmbeddingsData, callbacks):
            return self.embeddings(data, callbacks)

        return _embed_with_retry(data, callbacks)

    def embeddings(self, data: EmbeddingsData, callbacks):
        try:
            import google.generativeai as genai

            documents_embeddings = [genai.generate_embeddings(
                model=data.configs.provider_model, text=text)["embedding"] for text in data.embeddings_inputs]
            data.response = documents_embeddings

            return data
        except Exception as e:
            raise e
