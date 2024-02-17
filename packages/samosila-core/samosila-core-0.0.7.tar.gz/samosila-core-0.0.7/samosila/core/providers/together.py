import httpx
from typing import Any, Dict, List, Literal, Optional, Union


from ..types import (
    CallbackManager, Callbacks, ChatMessages, ImageData,
    ProviderBase, BaseMessage, ManipulationManager, ImageContent,
    Manipulations, TogetherInput, image_generation_decorator,
    ChatData, CompletionData, create_base_retry_decorator,
    Message, completion_decorator, chat_decorator
)


class TogetherAIError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        self.request = httpx.Request(
            method="POST", url="https://api.together.xyz/inference")
        self.response = httpx.Response(
            status_code=status_code, request=self.request)
        super().__init__(
            self.message
        )  # Call the base class constructor with the parameters it needs


class TogetherProvider(ProviderBase):

    def __init__(self, configs: TogetherInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate()
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: TogetherInput = configs

    @classmethod
    def model_validate(cls):
        try:
            import together
        except ImportError:
            raise ImportError(
                "Could not import together python package. "
                "Please install it with `pip install together`."
            )

    @completion_decorator
    def completion(
        self,
        prompt: Message,
        data: Optional[CompletionData] = None,
        configs: Optional[TogetherInput] = None,
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
        configs: Optional[TogetherInput] = None,
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

    def base_message_to_prompt(self, messages: List[BaseMessage]):
        prompt = ""
        added_prefix = False
        for message in messages:
            if message.role == "system":
                prompt += f"<s> <<SYS>> {message.content} <</SYS>>\\n\\n"
                added_prefix = True
            elif message.role == "human" or message.role == "user":
                prompt += f"{'' if added_prefix == True else '<s> [INST]'} {message.content} [/INST]"
            elif message.role == "chat" or message.role == "ai" or message.role == "assisstant":
                prompt += f"{message.content} </s>"
        return prompt

    def chat_with_retry(self, data: Union[CompletionData, ChatData], callbacks) -> Any:
        """Use tenacity to retry the completion call."""
        retry_decorator = create_base_retry_decorator([])

        @retry_decorator
        def _chat_with_retry(data: Union[CompletionData, ChatData], callbacks) -> Any:
            return self.generate(data, callbacks)

        return _chat_with_retry(data, callbacks)

    def generate(self, data: Union[CompletionData, ChatData], callbacks):
        try:
            import together

            prompt = ''
            if isinstance(data, ChatData):
                prompt = self.base_message_to_prompt(data.messages)
            else:
                prompt = data.prompt.content

            if data.configs.streaming is True:
                response_llm = ''
                for token in together.Complete.create_streaming(
                    prompt=prompt,
                    model=data.configs.provider_model,
                    api_key=data.configs.api_key,
                    max_tokens=data.configs.max_tokens,
                    top_k=data.configs.top_k,
                    top_p=data.configs.top_p,
                    temperature=data.configs.temperature,
                    repetition_penalty=data.configs.repeat_penalty,
                ):
                    if isinstance(token, str):
                        response_llm += token
                        self.callback_manager.on_llm_new_token(
                            token, callbacks)
                data = self.data_to_response(data, response_llm)
            else:
                res = together.Complete.create(
                    prompt=prompt or '',
                    model=data.configs.provider_model,
                    api_key=data.configs.api_key,
                    max_tokens=data.configs.max_tokens,
                    top_k=data.configs.top_k,
                    top_p=data.configs.top_p,
                    temperature=data.configs.temperature,
                    repetition_penalty=data.configs.repeat_penalty,
                )
                if isinstance(res, Dict):
                    data = self.data_to_response(
                        data=data,
                        text=res["output"]["choices"][0].get('text'),
                        model=res.get("model"),
                        uuid=res["output"].get("request_id"),
                    )
                    data.metadata["tags"] = res.get("tags")
                    data.metadata["status"] = res.get('status')
            return data
        except Exception as e:
            raise e

    @image_generation_decorator
    def image_generation(
        self,
        prompt: str,
        size: Literal['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792'],
        data: Optional[ImageData] = None,
        configs: Optional[TogetherInput] = None,
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
            import together

            width, height = data.size.split('x')
            response = together.Image.create(
                prompt=data.prompt,
                steps=data.steps,
                model=data.configs.provider_model,
                results=data.configs.n,
                negative_prompt=data.negative_prompt,
                height=int(height),
                width=int(width),
            )

            res: List[ImageContent] = []
            if isinstance(response, dict):
                for image in response["output"]["choices"]:
                    res.append(ImageContent(b64_json=image["image_base64"]))

            data.response = res

            return data
        except Exception as e:
            raise e
