import functools
import random
import string
import time
from typing import Any, Callable, Dict, List, Literal, Optional, Type, Union

import numpy as np
from pydantic import ConfigDict

from .utils import num_tokens_from_string
from .provider_inputs import BaseProviderInput
from .manipulations import ManipulationManager, Manipulations
from .callbacks import CallbackManager, Callbacks
from .response_types import (
    AssisstsntMessage,
    BaseMessage,
    ChatChoices,
    ChatContent,
    ChatResponse,
    CompletionChoices,
    EmbeddingsData,
    FunctionCallContent,
    ImageData,
    Message,
    ChatMessages,
    CompletionData,
    ChatData,
    TTSData,
    TranscriptionData,
    Usage,
)


class ProviderBase:

    model_config = ConfigDict(validate_assignment=True)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)

    configs: BaseProviderInput
    callback_manager: CallbackManager
    manipulation_manager: Optional[ManipulationManager] = None

    def __init__(self, configs: BaseProviderInput, callback_manager: CallbackManager, manipulation_manager: Optional[ManipulationManager] = None):
        self.manipulation_manager = manipulation_manager
        self.callback_manager = callback_manager
        self.configs = configs

    def completion(
        self,
        prompt: Message,
        data: Optional[CompletionData] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ) -> CompletionData:
        raise NotImplementedError()

    def chat(
        self,
        messages: ChatMessages,
        data: Optional[ChatData] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ) -> ChatData:
        raise NotImplementedError()

    def embedding(
        self,
        texts: List[str],
        data: Optional[EmbeddingsData] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ) -> EmbeddingsData:
        raise NotImplementedError()

    def image_generation(
        self,
        prompt: str,
        size: str,
        data: Optional[ImageData] = None,
        negative_prompt: Optional[str] = None,
        steps: Optional[int] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ) -> ImageData:
        raise NotImplementedError()

    def transcription(
        self,
        audio: str,
        data: Optional[TranscriptionData] = None,
        input_type: Literal["b64_json", "url"] = "b64_json",
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ) -> TranscriptionData:
        raise NotImplementedError()

    def data_to_response(
        self,
        data: Union[CompletionData, ChatData],
        text: str,
        model: Optional[str] = None,
        function: Optional[FunctionCallContent] = None,
        uuid: Optional[str] = None,
        created: Optional[int] = None,
        usage: Optional[Usage] = None,
    ):

        data.provider_model = model or self.configs.provider_model
        data.uuid = uuid or data.metadata.get("run_id")
        data.created = created or int(time.time())
        data.usage = usage
        if data.usage is None:
            prompt_tokens = num_tokens_from_string(data.prompt.content if isinstance(
                data, CompletionData) else "".join([x.content for x in data.messages]))
            completion_tokens = num_tokens_from_string(text)
            data.usage = Usage(
                completion_tokens=completion_tokens,
                prompt_tokens=prompt_tokens,
                total_tokens=completion_tokens + prompt_tokens,
            )
        if isinstance(data, ChatResponse):
            data.messages_response = [
                AssisstsntMessage(
                    content=text, additional_kwargs={"function_call": function}
                )
            ]
            data.response = [
                ChatChoices(
                    index=0,
                    finish_reason='stop',
                    message=ChatContent(
                        content=text,
                        role='assistant',
                        function_call=function
                    )
                )
            ]
        else:
            data.messages_response = [AssisstsntMessage(content=text)]
            data.response = [
                CompletionChoices(
                    text=text,
                    finish_reason='stop',
                    index=0,
                )
            ]
        return data


completion_type = Callable[[Any, Message, Optional[CompletionData],
                            Manipulations, Callbacks, Dict[str, Any]], CompletionData | None]

chat_type = Callable[[Any, ChatMessages, Optional[ChatData],
                      Manipulations, Callbacks, Dict[str, Any]], ChatData | None]

embeddings_type = Callable[[Any, List[str], Optional[EmbeddingsData],
                            Manipulations, Callbacks, Dict[str, Any]], EmbeddingsData | None]

image_generation_type = Callable[[Any, str, Literal['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792'],
                                  Optional[ImageData], Optional[str], Optional[int],
                                  Manipulations, Callbacks, Dict[str, Any]], ImageData | None]


def completion_decorator(func):
    @functools.wraps(func)
    def wrapper(
        self: Type[ProviderBase],
        prompt: Message,
        data: Optional[CompletionData] = None,
        configs: Optional[BaseProviderInput] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
        **kwargs
    ):
        if not issubclass(type(self), ProviderBase):
            raise TypeError("Class must extend ProviderBase")

        metadata["run_id"] = "opfr-" + "".join(random.choices(
            string.ascii_letters + string.digits, k=28))

        if isinstance(prompt, str):
            prompt = BaseMessage(content=prompt, role="user")
        if data is None:
            data = CompletionData(
                prompt=prompt,
                configs=configs or self.configs,
                metadata=metadata,
            )
        if data.configs is None:
            data.configs = configs or self.configs
        data.update(
            prompt=prompt,
            provider_model=self.configs.provider_model,
            metadata=metadata,
        )
        if self.manipulation_manager:
            data = self.manipulation_manager.on_llm_start(
                data, manipulations)
        self.callback_manager.on_llm_start(data, callbacks)

        if self.configs.cache == False or data.response is None:
            data = func(self, prompt, data, manipulations,
                        callbacks, metadata)
        else:
            data.metadata["caching"] = True

        if self.manipulation_manager:
            data = self.manipulation_manager.on_llm_end(
                data, manipulations)
        self.callback_manager.on_llm_end(data, callbacks)
        return data
    return wrapper


def chat_decorator(func):
    @functools.wraps(func)
    def wrapper(
        self: Type[ProviderBase],
        messages: ChatMessages,
        data: Optional[ChatData] = None,
        configs: Optional[BaseProviderInput] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ):
        metadata["run_id"] = "opfr-" + "".join(random.choices(
            string.ascii_letters + string.digits, k=28))

        _messages = []
        for message in messages:
            if isinstance(message, Dict):
                message = BaseMessage(
                    content=message["content"],
                    role=message["type"] or message["role"]
                )
            _messages.append(message)
        if data is None:
            data = ChatData(
                messages=_messages,
                configs=configs or self.configs,
                provider_model=self.configs.provider_model,
                metadata=metadata,
            )
        if data.configs is None:
            data.configs = configs or self.configs
        data.update(
            messages=_messages,
            provider_model=self.configs.provider_model,
            metadata=metadata,
        )
        if self.manipulation_manager:
            data = self.manipulation_manager.on_chat_start(
                data, manipulations)
        self.callback_manager.on_chat_start(data, callbacks)

        if self.configs.cache == False or data.response is None:
            data = func(self, messages, data,
                        manipulations, callbacks, metadata)
        else:
            data.metadata["caching"] = True

        if self.manipulation_manager:
            data = self.manipulation_manager.on_chat_end(
                data, manipulations)
        self.callback_manager.on_chat_end(data, callbacks)
        return data
    return wrapper


def embeddings_decorator(func):
    @functools.wraps(func)
    def wrapper(
        self: Type[ProviderBase],
        texts: List[str],
        data: Optional[EmbeddingsData] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ):
        metadata["run_id"] = "opfr-" + "".join(random.choices(
            string.ascii_letters + string.digits, k=28))

        if data is None:
            data = EmbeddingsData(
                embeddings_inputs=texts,
                provider_model=self.configs.provider_model,
                metadata=metadata,
            )
        data.update(
            embeddings_inputs=texts,
            provider_model=self.configs.provider_model,
            metadata=metadata,
        )
        if self.manipulation_manager:
            data = self.manipulation_manager.on_embeddings_start(
                data, manipulations)
        self.callback_manager.on_embeddings_start(data, callbacks)

        if self.configs.cache == False or data.response is None:
            data = func(self, texts, data, manipulations, callbacks, metadata)
        else:
            data.metadata["caching"] = True

        if self.manipulation_manager:
            data = self.manipulation_manager.on_embeddings_end(
                data, manipulations)
        self.callback_manager.on_embeddings_end(data, callbacks)
        return data

    return wrapper


def image_generation_decorator(func):
    @functools.wraps(func)
    def wrapper(
        self: Type[ProviderBase],
        prompt: str,
        size: Literal['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792'],
        data: Optional[ImageData] = None,
        configs: Optional[BaseProviderInput] = None,
        negative_prompt: Optional[str] = None,
        steps: Optional[int] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ):
        metadata["run_id"] = "opfr-" + "".join(random.choices(
            string.ascii_letters + string.digits, k=28))

        if data is None:
            data = ImageData(
                prompt=prompt,
                size=size,
                negative_prompt=negative_prompt,
                steps=steps,
                configs=configs or self.configs,
                provider_model=self.configs.provider_model,
                response_format=metadata.get(
                    "response_format") or "b64_json",
                metadata=metadata,
            )
        if data.configs is None:
            data.configs = configs or self.configs
        data.update(
            prompt=prompt,
            size=size,
            negative_prompt=negative_prompt,
            steps=steps,
            provider_model=self.configs.provider_model,
            response_format=metadata.get(
                "response_format") or "b64_json",
            metadata=metadata,
        )
        if self.manipulation_manager:
            data = self.manipulation_manager.on_image_start(
                data, manipulations)
        self.callback_manager.on_image_start(data, callbacks)

        if self.configs.cache == False or data.response is None:
            data = func(self, prompt, size, data, negative_prompt,
                        steps, manipulations, callbacks, metadata)
        else:
            data.metadata["caching"] = True

        if self.manipulation_manager:
            data = self.manipulation_manager.on_image_end(
                data, manipulations)
        self.callback_manager.on_image_end(data, callbacks)
        return data

    return wrapper


def tts_decorator(func):
    @functools.wraps(func)
    def wrapper(
        self: Type[ProviderBase],
        text: str,
        data: Optional[TTSData] = None,
        gender: Literal["Male", "Female"] = "Male",
        file_name: Optional[str] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ):
        metadata["run_id"] = "opfr-" + "".join(random.choices(
            string.ascii_letters + string.digits, k=28))

        if data is None:
            data = TTSData(
                text=text,
                download_path=file_name,
                gender=gender,
                provider_model=self.configs.provider_model,
                response_format=metadata.get(
                    "response_format") or "b64_json",
                metadata=metadata,
            )

        if self.manipulation_manager:
            data = self.manipulation_manager.on_tts_start(
                data, manipulations)
        self.callback_manager.on_tts_start(data, callbacks)

        if self.configs.cache == False or data.response is None:
            data = func(self, text, data, gender, file_name,
                        manipulations, callbacks, metadata)
        else:
            data.metadata["caching"] = True

        if self.manipulation_manager:
            data = self.manipulation_manager.on_tts_end(
                data, manipulations)
        self.callback_manager.on_tts_end(data, callbacks)
        return data

    return wrapper


def transcription_decorator(func):
    @functools.wraps(func)
    def wrapper(
        self: Type[ProviderBase],
        audio: str | np.ndarray,
        data: Optional[TranscriptionData] = None,
        input_type: Literal["b64_json", "url", "numpy"] = "b64_json",
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ):
        metadata["run_id"] = "opfr-" + "".join(random.choices(
            string.ascii_letters + string.digits, k=28))

        if data is None:
            data = TranscriptionData(
                audio=audio,
                input_type=input_type,
                provider_model=self.configs.provider_model,
                metadata=metadata,
            )

        if self.manipulation_manager:
            data = self.manipulation_manager.on_transcription_start(
                data, manipulations)
        self.callback_manager.on_transcription_start(data, callbacks)

        if self.configs.cache == False or data.response is None:
            data = func(self, audio, data, input_type,
                        manipulations, callbacks, metadata)
        else:
            data.metadata["caching"] = True

        if self.manipulation_manager:
            data = self.manipulation_manager.on_transcription_end(
                data, manipulations)
        self.callback_manager.on_transcription_end(data, callbacks)
        return data

    return wrapper
