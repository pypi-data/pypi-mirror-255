from typing import Any, Dict, Iterator, Optional, Union

from ..types import (
    CallbackManager, Callbacks, ChatMessages, chat_decorator,
    ProviderBase, Message, ManipulationManager, FunctionCallContent,
    Manipulations, LlamacppInput, completion_decorator,
    ChatData, CompletionData, create_base_retry_decorator
)


class LlamacppProvider(ProviderBase):

    def __init__(self, configs: LlamacppInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.client = self.model_validate(configs)
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: LlamacppInput = configs

    @classmethod
    def model_validate(cls, configs: LlamacppInput):
        try:
            from llama_cpp import Llama, LlamaGrammar
        except ImportError:
            raise ImportError(
                "Could not import llama-cpp-python library. "
                "Please install the llama-cpp-python library to "
                "use this embedding model: pip install llama-cpp-python"
            )

        try:
            client = Llama(
                model_path=configs.provider_model,
                f16_kv=configs.f16_kv,
                n_ctx=configs.n_ctx or 1024,
                n_gpu_layers=configs.n_gpu_layers,
                n_threads=configs.n_threads,
                chat_format=configs.chat_format,
                verbose=configs.verbose,
            )

            return client
        except Exception as e:
            raise ValueError(
                f"Could not load Llama model from path: {configs.provider_model}. "
                f"Received error {e}"
            )

    @completion_decorator
    def completion(
        self,
        prompt: Message,
        data: Optional[CompletionData] = None,
        configs: Optional[LlamacppInput] = None,
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
        configs: Optional[LlamacppInput] = None,
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
        retry_decorator = create_base_retry_decorator([])

        @retry_decorator
        def _chat_with_retry(data: Union[CompletionData, ChatData], callbacks) -> Any:
            return self.generate(data, callbacks)

        return _chat_with_retry(data, callbacks)

    def generate(self, data: Union[CompletionData, ChatData], callbacks):
        try:
            from llama_cpp import LlamaGrammar, ChatCompletionFunction, CreateCompletionResponse, CreateChatCompletionResponse

            if isinstance(data, ChatData):
                messages = []
                for message in data.messages:
                    message = message.to_message_dict()
                    messages.append(message)
                functions = []
                for func in (data.functions or []):
                    functions.append(
                        ChatCompletionFunction(
                            name=func.name,
                            description=func.description,
                            parameters=func.parameters,
                        )
                    )
                res = self.client.create_chat_completion(
                    messages=messages,
                    functions=functions,
                    repeat_penalty=data.configs.repeat_penalty or 1.1,
                    grammar=LlamaGrammar.from_string(
                        data.configs.grammer) if data.configs.grammer is not None else None,
                    max_tokens=data.configs.max_tokens,
                    top_k=data.configs.top_k or 40,
                    top_p=data.configs.top_p or 0.95,
                    temperature=data.configs.temperature or 0.4,
                    stop=data.configs.stop,
                    stream=data.configs.streaming
                )
                if isinstance(res, Iterator) == False:
                    if res["choices"][0]["message"].get("function_call") is not None:
                        data.metadata["response_functions"] = FunctionCallContent(
                            arguments=res["choices"][0]["message"]["function_call"]["arguments"],
                            name=res["choices"][0]["message"]["function_call"]["name"],
                        )
                    data = self.data_to_response(
                        data=data,
                        text=res["choices"][0]["message"].get("content") or '',
                        function=data.metadata.get("response_functions")
                    )
                else:
                    response_llm = ''
                    function = FunctionCallContent(
                        name='',
                        arguments=''
                    )
                    for token in res:
                        if token["choices"][0]["delta"].get("content") is not None:
                            # type: ignore
                            response_llm += token["choices"][0]["delta"]["content"]
                            self.callback_manager.on_llm_new_token(
                                token["choices"][0]["delta"]["content"], callbacks)  # type: ignore
                        if token["choices"][0]["delta"].get("function_call") is not None:
                            # type: ignore
                            function.name += token["choices"][0]["delta"]["function_call"]["name"]
                            # type: ignore
                            function.arguments += token["choices"][0]["delta"]["function_call"]["arguments"]
                    data = self.data_to_response(
                        data=data,
                        text=response_llm,
                        function=function
                    )

            else:
                res = self.client.create_completion(
                    prompt=data.prompt.content,
                    repeat_penalty=data.configs.repeat_penalty or 1.1,
                    grammar=LlamaGrammar.from_string(
                        data.configs.grammer) if data.configs.grammer is not None else None,
                    max_tokens=data.configs.max_tokens,
                    top_k=data.configs.top_k or 40,
                    top_p=data.configs.top_p or 0.95,
                    temperature=data.configs.temperature or 0.4,
                    stop=data.configs.stop,
                    stream=data.configs.streaming
                )
                if isinstance(res, Iterator) == False:
                    data = self.data_to_response(
                        data=data,
                        text=res["choices"][0]["text"]
                    )
                else:
                    response_llm = ''
                    for token in res:
                        response_llm += token["choices"][0]["text"] or ''
                        self.callback_manager.on_llm_new_token(
                            token["choices"][0]["text"] or '', callbacks)
                    data = self.data_to_response(
                        data=data,
                        text=response_llm,
                    )

            return data
        except Exception as e:
            raise e
