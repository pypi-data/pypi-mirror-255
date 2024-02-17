from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, model_validator


class BaseProviderInput(BaseModel):
    
    model_config = ConfigDict(validate_assignment=True)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)
    
    provider_model: str
    cache: bool = False
    verbose: bool = False
    max_retries: int = 4
    streaming: bool = False
    provider_kwargs: Dict[str, Any] = {}

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Dict:
        if values.get("max_tokens") is not None and values["max_tokens"] <= 0:
            raise ValueError("max_tokens must be positive")

        if values.get("temperature") is not None and not 0 <= values["temperature"] <= 1:
            raise ValueError("temperature must be in the range [0.0, 1.0]")

        if values.get("top_p") is not None and not 0 <= values["top_p"] <= 1:
            raise ValueError("top_p must be in the range [0.0, 1.0]")

        if values.get("top_k") is not None and values["top_k"] <= 0:
            raise ValueError("top_k must be positive")

        return values


class FakeInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'fake'
    chat_response: str | None = None
    completion_response: str | None = None
    function_call_response: str | None = None

class FireworksInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'fireworks'
    api_key: str | None = None


class HuggingFaceInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'huggingface'
    class_type: Optional[str] = None
    multi_process: bool = False
    cache_folder: Optional[str] = None
    device: str = "cpu"


class CTranslateInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'ctranslate2'
    device: str = "cpu"


class VoyageInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'voyage'
    api_key: str


class GradientInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'gradient'
    api_key: str
    workspace_id: Optional[str] = None


class NovitaInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'novita'
    api_key: str
    sampler_name: str = "DPM++ 2M Karras"
    n: int = 1
    cfg: float = 6

class SegmindInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'segmind'
    api_key: str
    sampler_name: str = "DPM++ 2M Karras"
    n: int = 1
    cfg: float = 6


class GoogleGenAIInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'generativeai'
    api_key: str
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    temperature: Optional[float] = None


class CohereInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'cohere'
    api_key: str
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class OpenAIInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'openai'
    api_key: str
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    max_tokens: Optional[int] = None
    base_url: Optional[str] = None
    stop: Optional[List[str]] = None
    base_url: Optional[str] = None
    n: int = 1


class TogetherInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'together'
    api_key: str
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    repeat_penalty: Optional[float] = None
    max_tokens: Optional[int] = None
    n: int = 1


class TTSInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'tts'
    emotion: Optional[str] = "Neutral"
    api_key: Optional[str] = None


class FasterWhisperInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'faster-whisper'
    emotion: Optional[str] = "Neutral"
    api_key: Optional[str] = None


class LlamacppInput(BaseProviderInput):
    provider_name: ClassVar[str] = 'llamacpp'
    top_k: Optional[int] = None
    chat_format: str = 'llama-2'
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    n_ctx: Optional[int] = None
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = None
    repeat_penalty: Optional[float] = None
    grammer: str | None = None
    f16_kv: bool = True
    n_gpu_layers: int = 0
    n_threads: int = 4


class CompleteInput(LlamacppInput, TogetherInput, OpenAIInput, CohereInput, CTranslateInput, SegmindInput,
        NovitaInput, FireworksInput, GoogleGenAIInput, VoyageInput, HuggingFaceInput, TTSInput, FasterWhisperInput,
        FakeInput):
    provider_name: ClassVar[str] = 'random'


class ProviderType(Enum):
    AI21 = "ai21"
    COHERE = "cohere"
    FAKE = "fake"
    FIREWORKS = "fireworks"
    FREE = "free"
    LLAMACPP = "llamacpp"
    OPENAI = "openai"
    PALM = "palm"
    TOGETHER = "together"

    @classmethod
    def get_type(cls, type: str):
        type_enum_value = None
        for enum_value in ProviderType:
            if type == enum_value.value:
                type_enum_value = enum_value
                break
        return type_enum_value or cls.FREE
