from typing import Any, Dict, List, Optional, Union

from .states import FeaturesState
from .response_types import (
    CompletionData, 
    ChatData,
    EmbeddingsData,
    ImageData,
    TTSData,
    TranscriptionData
)


class ManipulationHandler:

    def __init__(self, features_state: FeaturesState = FeaturesState(), **kwargs):
        self.features_state = features_state
        pass

    def on_llm_start(self, data: CompletionData, **kwargs) -> CompletionData:
        return data

    def on_llm_end(self, data: CompletionData, **kwargs) -> CompletionData:
        return data

    def on_chat_start(self, data: ChatData, **kwargs) -> ChatData:
        return data

    def on_chat_end(self, data: ChatData, **kwargs) -> ChatData:
        return data

    def on_llm_response(self, data: Union[CompletionData, ChatData], **kwargs) -> Union[CompletionData, ChatData]:
        return data

    def on_llm_new_token(self, token: str, **kwargs):
        return token

    def on_embeddings_start(self,  data: EmbeddingsData, **kwargs) -> EmbeddingsData:
        return data

    def on_embeddings_end(self,  data: EmbeddingsData, **kwargs) -> EmbeddingsData:
        return data

    def on_image_start(self,  data: ImageData, **kwargs):
        return data

    def on_image_end(self,  data: ImageData, **kwargs):
        return data

    def on_tts_start(self,  data: TTSData, **kwargs):
        return data

    def on_tts_end(self,  data: TTSData, **kwargs):
        return data

    def on_transcription_start(self,  data: TranscriptionData, **kwargs):
        return data

    def on_transcription_end(self,  data: TranscriptionData, **kwargs):
        return data


Manipulations = Optional[List[ManipulationHandler]]


def manipulation_from_feature(feature: str, manipulations: List[ManipulationHandler]):
    res: List[ManipulationHandler] = []
    for manipulation in manipulations:
        if manipulation.features_state.model_dump()[feature] == True:
            res.append(manipulation)
    return res


class ManipulationManager:
    def __init__(self, handlers: List[ManipulationHandler], features_state: FeaturesState = FeaturesState(), **kwargs):
        self.features_state = features_state
        self.handlers = handlers

    def on_llm_start(self, data: CompletionData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_llm_start == False:
            return data
        handlers = manipulation_from_feature(
            'on_llm_start', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_llm_start(data, kwargs=kwargs)
        return data

    def on_llm_end(self, data: CompletionData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_llm_end == False:
            return data
        handlers = manipulation_from_feature(
            'on_llm_end', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_llm_end(data, kwargs=kwargs)
        return data

    def on_chat_start(self, data: ChatData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_chat_start == False:
            return data
        handlers = manipulation_from_feature(
            'on_chat_start', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_chat_start(data, kwargs=kwargs)
        return data

    def on_chat_end(self, data: ChatData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_chat_end == False:
            return data
        handlers = manipulation_from_feature(
            'on_chat_end', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_chat_end(data, kwargs=kwargs)
        return data

    def on_llm_response(self, data: Union[CompletionData, ChatData], manipulations: Manipulations, **kwargs):
        if self.features_state.on_llm_response == False:
            return data
        handlers = manipulation_from_feature(
            'on_llm_response', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_llm_response(data, kwargs=kwargs)
        return data

    def on_llm_new_token(self, token: str, manipulations: Manipulations, **kwargs):
        if self.features_state.on_llm_new_token == False:
            return token
        handlers = manipulation_from_feature(
            'on_llm_new_token', self.handlers + (manipulations or []))
        for handler in handlers:
            token = handler.on_llm_new_token(token, kwargs=kwargs)
        return token

    def on_embeddings_start(self, data: EmbeddingsData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_embeddings_start == False:
            return data
        handlers = manipulation_from_feature(
            'on_embeddings_start', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_embeddings_start(data, kwargs=kwargs)
        return data

    def on_embeddings_end(self, data: EmbeddingsData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_embeddings_end == False:
            return data
        handlers = manipulation_from_feature(
            'on_embeddings_end', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_embeddings_end(data, kwargs=kwargs)
        return data

    def on_image_start(self, data: ImageData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_image_start == False:
            return data
        handlers = manipulation_from_feature(
            'on_image_start', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_image_start(data, kwargs=kwargs)
        return data

    def on_image_end(self, data: ImageData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_image_end == False:
            return data
        handlers = manipulation_from_feature(
            'on_image_end', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_image_end(data, kwargs=kwargs)
        return data

    def on_tts_start(self, data: TTSData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_tts_start == False:
            return data
        handlers = manipulation_from_feature(
            'on_tts_start', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_tts_start(data, kwargs=kwargs)
        return data

    def on_tts_end(self, data: TTSData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_tts_end == False:
            return data
        handlers = manipulation_from_feature(
            'on_tts_end', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_tts_end(data, kwargs=kwargs)
        return data

    def on_transcription_start(self, data: TranscriptionData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_transcription_start == False:
            return data
        handlers = manipulation_from_feature(
            'on_transcription_start', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_transcription_start(data, kwargs=kwargs)
        return data

    def on_transcription_end(self, data: TranscriptionData, manipulations: Manipulations, **kwargs):
        if self.features_state.on_transcription_end == False:
            return data
        handlers = manipulation_from_feature(
            'on_transcription_end', self.handlers + (manipulations or []))
        for handler in handlers:
            data = handler.on_transcription_end(data, kwargs=kwargs)
        return data
