from typing import Any, Dict, List, Literal, Optional, Set, Union

from ..types import (
    CallbackManager, Callbacks, ChatMessages, EmbeddingsData,
    ProviderBase, Message, ManipulationManager, FunctionCallContent,
    Manipulations, OpenAIInput, image_generation_decorator, completion_decorator,
    ChatData, CompletionData, create_base_retry_decorator, FunctionCall,
    Usage, ImageData, ImageContent, embeddings_decorator, chat_decorator
)


def update_token_usage(
    keys: Set[str], response: Dict[str, Any], token_usage: Dict[str, Any]
) -> None:
    """Update token usage."""
    _keys_to_use = keys.intersection(response["usage"])
    for _key in _keys_to_use:
        if _key not in token_usage:
            token_usage[_key] = response["usage"][_key]
        else:
            token_usage[_key] += response["usage"][_key]


class OpenAIProvider(ProviderBase):

    def __init__(self, configs: OpenAIInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate()
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: OpenAIInput = configs

    @classmethod
    def model_validate(cls):
        try:
            import openai
        except ImportError:
            raise ImportError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )

    @completion_decorator
    def completion(
        self,
        prompt: Message,
        data: Optional[CompletionData] = None,
        configs: Optional[OpenAIInput] = None,
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
        configs: Optional[OpenAIInput] = None,
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
        import openai

        errors = [
            openai.Timeout,
            openai.APIError,
            openai.APIConnectionError,
            openai.RateLimitError,
        ]
        retry_decorator = create_base_retry_decorator(
            error_types=errors, max_retries=data.configs.max_retries, run_manager=self.callback_manager
        )

        @retry_decorator
        def _chat_with_retry(data: Union[CompletionData, ChatData], callbacks) -> Any:
            return self.generate(data, callbacks)

        return _chat_with_retry(data, callbacks)

    def generate(self, data: Union[CompletionData, ChatData], callbacks):
        try:
            from openai import OpenAI
            
            client = OpenAI(
                base_url=data.configs.base_url,
                api_key=data.configs.api_key,
            )

            if isinstance(data, ChatData):
                messages = []
                functions: List[FunctionCall] = []
                for message in (data.messages):
                    dic = message.to_message_dict()
                    messages.append(dic)
                    function = message.function_call()
                    if function is not None:
                        functions.append(function)
                if data.functions is not None:
                    functions.extend(data.functions)
                if data.configs.streaming is True:
                    response_llm: str = ""
                    function = FunctionCallContent(
                        name='',
                        arguments=''
                    )

                    for token in client.chat.completions.create(
                        messages=messages,
                        functions=self.function_call_to_openai(functions) if len(functions) > 0 else None,
                        stream=True,
                        model=data.configs.provider_model,
                        extra_headers=data.configs.provider_kwargs,
                        frequency_penalty=data.configs.frequency_penalty,
                        max_tokens=data.configs.max_tokens,
                        stop=data.configs.stop,
                        temperature=data.configs.temperature,
                        top_p=data.configs.top_p,
                        presence_penalty=data.configs.presence_penalty,
                    ):
                        if token.choices[0].delta is not None:
                            response_llm += token.choices[0].delta.content
                            if token.choices[0].delta.function_call is not None:
                                function.arguments += token.choices[0].delta.function_call.arguments
                                function.name += token.choices[0].delta.function_call.name
                            self.callback_manager.on_llm_new_token(
                                token.choices[0].delta.content, callbacks)
                    data = self.data_to_response(
                        data=data,
                        text=response_llm,
                        function=function
                    )
                else:
                    res = client.chat.completions.create(
                        messages=messages,
                        functions=self.function_call_to_openai(
                            functions) if len(functions) > 0 else None,
                        model=data.configs.provider_model,
                        extra_headers=data.configs.provider_kwargs,
                        frequency_penalty=data.configs.frequency_penalty,
                        max_tokens=data.configs.max_tokens,
                        stop=data.configs.stop,
                        temperature=data.configs.temperature,
                        top_p=data.configs.top_p,
                        presence_penalty=data.configs.presence_penalty,
                    )
                    if res.choices[0].message.function_call is not None:
                        data.metadata["response_functions"] = FunctionCallContent(
                            arguments=res.choices[0].message.function_call.arguments,
                            name=res.choices[0].message.function_call.name,
                        )
                    data = self.data_to_response(
                        data=data,
                        text=res.choices[0].message.content or '',
                        model=res.model,
                        uuid=res.id,
                        created=res.created,
                        function=data.metadata.get("response_functions"),
                        usage=Usage(completion_tokens=res.usage.completion_tokens,
                                    prompt_tokens=res.usage.prompt_tokens, total_tokens=res.usage.total_tokens) if res.usage is not None else None,
                    )
            else:
                prompt = data.prompt.content

                if data.configs.streaming is True:
                    response_llm = ''

                    for token in client.completions.create(
                        prompt=prompt,
                        stream=True,
                        model=data.configs.provider_model,
                        extra_headers=data.configs.provider_kwargs,
                        frequency_penalty=data.configs.frequency_penalty,
                        max_tokens=data.configs.max_tokens,
                        stop=data.configs.stop,
                        temperature=data.configs.temperature,
                        top_p=data.configs.top_p,
                    ):
                        response_llm += token.choices[0].text
                        self.callback_manager.on_llm_new_token(
                            token.choices[0].text, callbacks)
                    data = self.data_to_response(
                        data=data,
                        text=response_llm,
                    )
                else:
                    res = client.completions.create(
                        prompt=prompt,
                        model=data.configs.provider_model,
                        extra_headers=data.configs.provider_kwargs,
                        frequency_penalty=data.configs.frequency_penalty,
                        max_tokens=data.configs.max_tokens,
                        stop=data.configs.stop,
                        temperature=data.configs.temperature,
                        top_p=data.configs.top_p,
                    )
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

        retry_decorator = create_base_retry_decorator(
            [], max_retries=data.configs.max_retries, run_manager=self.callback_manager)

        @retry_decorator
        def _embed_with_retry(data: EmbeddingsData, callbacks) -> EmbeddingsData:
            return self.embeddings(data, callbacks)

        return _embed_with_retry(data, callbacks)

    def embeddings(self, data: EmbeddingsData, callbacks):
        try:
            from openai import OpenAI

            client = OpenAI(
                base_url=data.configs.base_url,
                api_key=data.configs.api_key,
            )

            documents_embeddings = client.embeddings.create(
                input=data.embeddings_inputs, model=data.configs.provider_model, encoding_format="float")
            data.response = [data.embedding for data in documents_embeddings.data]

            return data
        except Exception as e:
            raise e

    @image_generation_decorator
    def image_generation(
        self,
        prompt: str,
        size: Literal['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792'],
        data: Optional[ImageData] = None,
        configs: Optional[OpenAIInput] = None,
        negative_prompt: Optional[str] = None,
        steps: Optional[int] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ):
        try:
            if data is None:
                raise Exception("Decorator didnt Initialized Data")
            data = self.image_generations(data, callbacks)
            return data
        except Exception as e:
            raise e

    def image_generations(self, data: ImageData, callbacks):
        try:
            from openai import OpenAI

            client = OpenAI(
                base_url=data.configs.base_url,
                api_key=data.configs.api_key,
            )

            response = client.images.generate(
                prompt=data.prompt,
                model=data.configs.provider_model,
                n=data.configs.n,
                quality='standard',
                size=data.size,
                response_format=data.response_format,
            )

            res: List[ImageContent] = []
            if isinstance(response, dict):
                for image in response["data"]:
                    if image.get('url') is not None:
                        res.append(ImageContent(url=image["url"]))
                    if image.get('b64_json') is not None:
                        res.append(ImageContent(b64_json=image["b64_json"]))

            data.response = res

            return data
        except Exception as e:
            raise e

    def function_call_to_openai(self, functions: List[FunctionCall]):
        from openai.types.chat.completion_create_params import Function

        res: List[Function] = []        
        for function in functions:
            res.append(Function(
                name=function.name,
                parameters=function.parameters,
                description=function.description,
            ))
        return res
