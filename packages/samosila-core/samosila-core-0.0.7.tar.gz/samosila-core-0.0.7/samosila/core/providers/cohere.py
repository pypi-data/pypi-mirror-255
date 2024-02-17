from typing import Any, Dict, List, Optional, Union

from ..types import (
    CallbackManager, Callbacks, ChatMessages, chat_decorator, EmbeddingsData,
    ProviderBase, Message, ManipulationManager, Manipulations, CohereInput, embeddings_decorator,
    ChatData, CompletionData, create_base_retry_decorator, Usage, completion_decorator
)


class CohereProvider(ProviderBase):

    def __init__(self, configs: CohereInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.client = self.model_validate(configs)
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: CohereInput = configs

    @classmethod
    def model_validate(cls, configs: CohereInput):
        try:
            import cohere
        except ImportError:
            raise ImportError(
                "Could not import cohere python package. "
                "Please install it with `pip install cohere`."
            )

        return cohere.Client(configs.api_key)

    @completion_decorator
    def completion(
        self,
        prompt: Message,
        data: Optional[CompletionData] = None,
        configs: Optional[CohereInput] = None,
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
        configs: Optional[CohereInput] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
        **kwargs
    ) -> ChatData:
        try:
            if data is None:
                raise Exception("Decorator didnt Initialized Data")
            data = self.chat_with_retry(data, callbacks)
            return data
        except Exception as e:
            raise e

    def chat_with_retry(self, data: Union[CompletionData, ChatData], callbacks):
        import cohere

        retry_decorator = create_base_retry_decorator(
            [cohere.CohereError], max_retries=data.configs.max_retries, run_manager=self.callback_manager)

        @retry_decorator
        def _chat_with_retry(data: Union[CompletionData, ChatData], callbacks) -> ChatData | CompletionData:
            return self.generate(data, callbacks)

        return _chat_with_retry(data, callbacks)

    def generate(self, data: Union[CompletionData, ChatData], callbacks) -> ChatData | CompletionData:
        from cohere.responses.chat import Chat, StreamingChat
        from cohere.responses.generation import Generations, StreamingGenerations

        try:
            params = {
                "temperature":  data.configs.temperature,
                "max_tokens":  data.configs.max_tokens,
                "p":  data.configs.top_p,
                "k":  data.configs.top_k,
                "model": data.configs.provider_model,
                "stream": data.configs.streaming,
            }

            if isinstance(data, ChatData):
                messages = data.messages

                res: Chat | StreamingChat = self.client.chat(
                    message=messages[-1].content,
                    chat_history=[
                        {"role": x.role, "message": x.content} for x in messages[:-1]
                    ],
                    **params
                )
                if isinstance(res, StreamingChat):
                    response_llm = ''
                    for token in res:
                        if token.event_type == "text-generation":
                            response_llm += token.text
                            self.callback_manager.on_llm_new_token(
                                token.text, callbacks)
                    data = self.data_to_response(data, response_llm)
                else:
                    if res.token_count is not None:
                        data.metadata["usage"] = Usage(
                            completion_tokens=res.token_count.get(
                                "response_tokens"),
                            prompt_tokens=res.token_count.get("prompt_tokens"),
                            total_tokens=res.token_count.get("total_tokens")
                        )
                    data = self.data_to_response(
                        data=data,
                        text=res.text,
                        uuid=res.generation_id,
                        usage=data.metadata.get("usage")
                    )
            else:
                result: Generations | StreamingGenerations = self.client.generate(
                    prompt=data.prompt.content,
                    **params
                )
                if isinstance(result, StreamingGenerations):
                    response_llm = ''
                    for token in result:
                        response_llm += token.text
                        self.callback_manager.on_llm_new_token(
                            token.text, callbacks)
                    data = self.data_to_response(data, response_llm)
                else:
                    data = self.data_to_response(
                        data=data,
                        text=result.data[0].text,
                        uuid=result.data[0].id,
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
    ):
        try:
            data = self.embed_with_retry(data, callbacks)
            return data
        except Exception as e:
            raise e

    def embed_with_retry(self, data: EmbeddingsData, callbacks):

        retry_decorator = create_base_retry_decorator(
            [], max_retries=data.configs.max_retries, run_manager=self.callback_manager)

        @retry_decorator
        def _embed_with_retry(data: EmbeddingsData, callbacks):
            return self.embeddings(data, callbacks)

        return _embed_with_retry(data, callbacks)

    def embeddings(self, data: EmbeddingsData, callbacks):
        try:
            documents_embeddings = self.client.embed(
                data.embeddings_inputs, model=data.configs.provider_model, input_type="search_document")
            data.response = documents_embeddings.embeddings

            return data
        except Exception as e:
            raise e
