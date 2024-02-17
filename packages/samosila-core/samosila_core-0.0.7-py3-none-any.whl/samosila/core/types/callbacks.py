from typing import List, Optional, Union
from tenacity import RetryCallState

from .states import FeaturesState
from .response_types import (
    CompletionData, 
    ChatData,
    EmbeddingsData,
    ImageData,
    TTSData,
    TranscriptionData,
)

class CallbackHandler:

    def __init__(self, features_state: FeaturesState = FeaturesState(), **kwargs):
        self.features_state = features_state
        pass

    def on_llm_start(self, data: CompletionData, **kwargs):
        pass

    def on_llm_end(self, data: CompletionData, **kwargs):
        pass

    def on_chat_start(self, data: ChatData, **kwargs):
        pass

    def on_chat_end(self, data: ChatData, **kwargs):
        pass

    def on_llm_response(self, data: Union[CompletionData, ChatData], **kwargs):
        pass

    def on_llm_new_token(self, token: str, **kwargs):
        pass

    def on_embeddings_start(self,  data: EmbeddingsData, **kwargs):
        pass

    def on_embeddings_end(self,  data: EmbeddingsData, **kwargs):
        pass

    def on_image_start(self,  data: ImageData, **kwargs):
        pass

    def on_image_end(self,  data: ImageData, **kwargs):
        pass

    def on_tts_start(self,  data: TTSData, **kwargs):
        pass

    def on_tts_end(self,  data: TTSData, **kwargs):
        pass

    def on_transcription_start(self,  data: TranscriptionData, **kwargs):
        pass

    def on_transcription_end(self,  data: TranscriptionData, **kwargs):
        pass

    def on_retry(self, retry_state: RetryCallState, **kwargs):
        pass

Callbacks = Optional[List[CallbackHandler]]

def callback_from_feature(feature: str, callbacks: List[CallbackHandler]):
    res: List[CallbackHandler] = []
    for callback in callbacks:
        if callback.features_state.model_dump()[feature] == True:
            res.append(callback)
    return res

class CallbackManager:
    def __init__(self, handlers: List[CallbackHandler], features_state: FeaturesState = FeaturesState(), **kwargs):
        self.features_state = features_state
        self.handlers = handlers

    def on_llm_start(self, data: CompletionData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_llm_start == False:
            return
        handlers = callback_from_feature('on_llm_start', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_llm_start(data, kwargs=kwargs)

    def on_llm_end(self, data: CompletionData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_llm_end == False:
            return
        handlers = callback_from_feature(
            'on_llm_end', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_llm_end(data, kwargs=kwargs)

    def on_chat_start(self, data: ChatData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_chat_start == False:
            return
        handlers = callback_from_feature(
            'on_chat_start', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_chat_start(data, kwargs=kwargs)

    def on_chat_end(self, data: ChatData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_chat_end == False:
            return
        handlers = callback_from_feature(
            'on_chat_end', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_chat_end(data, kwargs=kwargs)

    def on_llm_response(self, data: Union[CompletionData, ChatData], callbacks: Callbacks, **kwargs):
        if self.features_state.on_llm_response == False:
            return
        handlers = callback_from_feature(
            'on_llm_response', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_llm_response(data, kwargs=kwargs)

    def on_llm_new_token(self, token: str, callbacks: Callbacks, **kwargs):
        if self.features_state.on_llm_new_token == False:
            return
        handlers = callback_from_feature(
            'on_llm_new_token', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_llm_new_token(token, kwargs=kwargs)

    def on_embeddings_start(self, data: EmbeddingsData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_embeddings_start == False:
            return
        handlers = callback_from_feature(
            'on_embeddings_start', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_embeddings_start(data, kwargs=kwargs)

    def on_embeddings_end(self, data: EmbeddingsData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_embeddings_end == False:
            return
        handlers = callback_from_feature(
            'on_embeddings_end', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_embeddings_end(data, kwargs=kwargs)

    def on_image_start(self, data: ImageData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_image_start == False:
            return
        handlers = callback_from_feature(
            'on_image_start', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_image_start(data, kwargs=kwargs)

    def on_image_end(self, data: ImageData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_image_end == False:
            return
        handlers = callback_from_feature(
            'on_image_end', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_image_end(data, kwargs=kwargs)

    def on_tts_start(self, data: TTSData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_tts_start == False:
            return
        handlers = callback_from_feature(
            'on_tts_start', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_tts_start(data, kwargs=kwargs)

    def on_tts_end(self, data: TTSData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_tts_end == False:
            return
        handlers = callback_from_feature(
            'on_tts_end', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_tts_end(data, kwargs=kwargs)

    def on_transcription_start(self, data: TranscriptionData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_transcription_start == False:
            return
        handlers = callback_from_feature(
            'on_transcription_start', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_transcription_start(data, kwargs=kwargs)

    def on_transcription_end(self, data: TranscriptionData, callbacks: Callbacks, **kwargs):
        if self.features_state.on_transcription_end == False:
            return
        handlers = callback_from_feature(
            'on_transcription_end', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_transcription_end(data, kwargs=kwargs)

    def on_retry(self, retry_state: RetryCallState, callbacks: Callbacks, **kwargs):
        if self.features_state.on_retry == False:
            return
        handlers = callback_from_feature('on_retry', self.handlers + (callbacks or []))
        for handler in handlers:
            handler.on_retry(retry_state, kwargs=kwargs)
