import time
from typing import Any, Dict, Optional, Union

from ..types import (
    CallbackManager, Callbacks, ChatMessages, chat_decorator,
    ProviderBase, Message, ManipulationManager,
    Manipulations, FakeInput, completion_decorator,
    CompletionData, create_base_retry_decorator, ChatData
)


class FakeProvider(ProviderBase):

    def __init__(self, configs: FakeInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.client = self.model_validate(configs)
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: FakeInput = configs

    @classmethod
    def model_validate(cls, configs: FakeInput):
        pass

    @completion_decorator
    def completion(
        self,
        prompt: Message,
        data: Optional[CompletionData] = None,
        configs: Optional[FakeInput] = None,
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
        configs: Optional[FakeInput] = None,
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
            res = data.configs.chat_response or data.configs.completion_response or "My tummy needs a yummy, Like a plummy tasty gummy. I'm in a slummy feeling crummy, Give me something in my tummy. Please don't treat me like a scummy, And don't look at me like a dummy. \n\n"
            if data.configs.streaming == True:
                for elem in res.split(" "):
                    self.callback_manager.on_llm_new_token(elem, callbacks)
                    time.sleep(0.1)
            if isinstance(data, ChatData):
                data.messages_response
            self.data_to_response(data, res)

            return data
        except Exception as e:
            raise e
