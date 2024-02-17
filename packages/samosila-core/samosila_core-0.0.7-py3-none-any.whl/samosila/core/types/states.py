from typing import Dict
from pydantic import BaseModel, ConfigDict


class FeaturesState(BaseModel):
    on_llm_start: bool = True
    on_llm_end: bool = True
    on_chat_start: bool = True
    on_chat_end: bool = True
    on_llm_response: bool = True
    on_llm_new_token: bool = True
    on_embeddings_start: bool = True
    on_embeddings_end: bool = True
    on_image_start: bool = True
    on_image_end: bool = True
    on_tts_start: bool = True
    on_tts_end: bool = True
    on_transcription_start: bool = True
    on_transcription_end: bool = True
    on_retry: bool = True
    
    model_config = ConfigDict(validate_assignment=True)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)
    
    @classmethod
    def only(cls, states: Dict[str, bool]):
        res = FeaturesState.none()
        for state in states.items():
            setattr(res, state[0], state[1])
        return res

    @classmethod
    def none(cls):
        res = FeaturesState(
            on_chat_end=False,
            on_chat_start=False,
            on_image_end=False,
            on_image_start=False,
            on_transcription_end=False,
            on_transcription_start=False,
            on_tts_end=False,
            on_tts_start=False,
            on_embeddings_end=False,
            on_embeddings_start=False,
            on_llm_end=False,
            on_llm_new_token=False,
            on_llm_response=False,
            on_llm_start=False,
            on_retry=False
        )
        return res

