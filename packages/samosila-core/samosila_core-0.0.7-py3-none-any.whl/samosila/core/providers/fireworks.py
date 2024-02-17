from typing import Any, Dict, Generator, Optional, Union

from ..types import (
    CallbackManager, Callbacks, ChatMessages,
    Manipulations, FireworksInput, completion_decorator,
    ChatData, CompletionData, create_base_retry_decorator,
    ProviderBase, Message, ManipulationManager,
    Usage, FunctionCallContent, chat_decorator
)


class FireworksProvider(ProviderBase):

    def __init__(self, configs: FireworksInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.client = self.model_validate(configs)
        super().__init__(configs, callback_manager, manipulation_manager)

    @classmethod
    def model_validate(cls, configs: FireworksInput):
        try:
            import fireworks.client
        except ImportError as e:
            raise ImportError(
                "Could not import fireworks-ai python package. "
                "Please install it with `pip install fireworks-ai`."
            ) from e
        fireworks.client.api_key = configs.api_key
        return fireworks.client

    @completion_decorator
    def completion(
        self,
        prompt: Message,
        data: Optional[CompletionData] = None,
        configs: Optional[FireworksInput] = None,
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
        configs: Optional[FireworksInput] = None,
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
            import fireworks.client

            if isinstance(data, ChatData):
                messages = []
                for message in data.messages:
                    message = message.to_message_dict()
                    messages.append(message)

                res = fireworks.client.ChatCompletion.create(
                    prompt_or_messages=messages,
                    model=data.configs.provider_model,
                    stream=data.configs.streaming,
                )
                if isinstance(res, Generator):
                    response_llm = ''
                    function = FunctionCallContent(
                        name='',
                        arguments=''
                    )
                    for token in res:
                        if token.choices[0].delta.function_call is not None:
                            function.arguments += token.choices[0].delta.function_call.arguments
                            function.name += token.choices[0].delta.function_call.name
                        if token.choices[0].delta.content is not None:
                            response_llm += token.choices[0].delta.content
                            self.callback_manager.on_llm_new_token(
                                token.choices[0].delta.content, callbacks)

                    data = self.data_to_response(
                        data, response_llm, function=function)
                else:
                    if res.choices[0].message.function_call is not None:
                        data.metadata["response_functions"] = FunctionCallContent(
                            arguments=res.choices[0].message.function_call.arguments,
                            name=res.choices[0].message.function_call.name,
                        )
                    data = self.data_to_response(
                        data=data,
                        text=res.choices[0].message.content,
                        model=res.model,
                        uuid=res.id,
                        created=res.created,
                        function=data.metadata.get("response_functions"),
                        usage=Usage(completion_tokens=res.usage.completion_tokens,
                                    prompt_tokens=res.usage.prompt_tokens, total_tokens=res.usage.total_tokens) if res.usage is not None else None,
                    )
            else:
                res = fireworks.client.Completion.create(
                    prompt_or_messages=data.prompt.content,
                    model=data.configs.provider_model,
                    stream=data.configs.streaming,
                )

                if isinstance(res, Generator):
                    response_llm = ''
                    for token in res:
                        response_llm += token.choices[0].text
                        self.callback_manager.on_llm_new_token(
                            token.choices[0].text, callbacks)

                    data = self.data_to_response(
                        data=data,
                        text=response_llm,
                    )

                else:
                    data = self.data_to_response(
                        data=data,
                        text=res.choices[0].text,
                        model=res.model,
                        uuid=res.id,
                        created=res.created,
                        usage=Usage(completion_tokens=res.usage.completion_tokens,
                                    prompt_tokens=res.usage.prompt_tokens, total_tokens=res.usage.total_tokens) if res.usage is not None else None,
                    )

            return data
        except Exception as e:
            raise e
