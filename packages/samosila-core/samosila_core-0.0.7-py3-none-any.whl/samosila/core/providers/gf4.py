from typing import Any, Dict, Generator, Optional, Union

from ..types import (
    CallbackManager, Callbacks, ChatMessages, chat_decorator,
    ProviderBase, Message, ManipulationManager,
    Manipulations, BaseProviderInput, completion_decorator,
    ChatData, CompletionData, create_base_retry_decorator
)


class FreeProvider(ProviderBase):

    def __init__(self, configs: BaseProviderInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate()
        super().__init__(configs, callback_manager, manipulation_manager)

    @classmethod
    def model_validate(cls):
        try:
            import g4f
        except ImportError:
            raise ImportError(
                "Could not import g4f python package. "
                "Please install it with `pip install g4f`."
            )

    @completion_decorator
    def completion(
        self,
        prompt: Message,
        data: Optional[CompletionData] = None,
        configs: Optional[BaseProviderInput] = None,
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
        configs: Optional[BaseProviderInput] = None,
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

        retry_decorator = create_base_retry_decorator(
            [], max_retries=data.configs.max_retries, run_manager=self.callback_manager)

        @retry_decorator
        def _chat_with_retry(data: Union[CompletionData, ChatData], callbacks) -> Any:
            return self.generate(data, callbacks)

        return _chat_with_retry(data, callbacks)

    def generate(self, data: Union[CompletionData, ChatData], callbacks):
        try:
            from g4f import ChatCompletion

            messages = []
            if isinstance(data, ChatData):
                for message in data.messages:
                    message = message.to_message_dict()
                    messages.append(message)
            else:
                messages.append(
                    {"role": "user", "content": data.prompt.content})

            res = ChatCompletion.create(
                messages=messages,
                model=data.configs.provider_model,
                stream=self.configs.streaming,
            )
            if isinstance(res, Generator):
                response_llm = ''
                for token in res:
                    response_llm += token
                    self.callback_manager.on_llm_new_token(
                        token, callbacks)
                data = self.data_to_response(
                    data=data,
                    text=response_llm,
                )
            else:
                data = self.data_to_response(
                    data=data,
                    text=res,
                )

            return data
        except Exception as e:
            raise e
