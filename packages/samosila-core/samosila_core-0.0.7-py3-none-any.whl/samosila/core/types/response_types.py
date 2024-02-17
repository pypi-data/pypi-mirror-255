
import numpy as np
from abc import ABC
from typing import Any, Dict, List, Literal, Optional, TypeVar, Union
from pydantic import BaseModel as _BaseModel, ConfigDict
from regex import F


class BaseModel(_BaseModel):
    
    model_config = ConfigDict(validate_assignment=True)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)


class FunctionCall(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class BaseMessage(BaseModel, ABC):
    
    model_config = ConfigDict(validate_assignment=True)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)

    def to_message_dict(self) -> Dict[str, str]:
        return {
            "content": self.content,
            "role": self.role,
        }

    def function_call(self) -> FunctionCall | None:
        function_call = self.additional_kwargs.get("function_call")
        if function_call is not None and isinstance(function_call, FunctionCall):
            return function_call

    def to_str(self) -> str:
        return self.content
    
    content: str
    role: str
    additional_kwargs: Dict[str, Any] = {}


class SystemMessage(BaseMessage):
    role: str = "system"


class HumanMessage(BaseMessage):
    role: str = "human"


class UserMessage(BaseMessage):
    role: str = "user"


class AIMessage(BaseMessage):
    role: str = "ai"

class AssisstsntMessage(BaseMessage):
    role: str = "assisstant"


Message = Union[BaseMessage, str]
ChatMessages = Union[List[BaseMessage], List[Dict[str, Any]]]


class Usage(BaseModel):
    completion_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost: Optional[int] = None


class CompletionChoices(BaseModel):
    finish_reason: str
    index: int
    text: str


class FunctionCallContent(BaseModel):
    name: str
    arguments: str


class ChatContent(BaseModel):
    content: Optional[str] = None
    function_call: Optional[FunctionCallContent] = None
    role: Optional[str] = None

class ImageContent(BaseModel):
    url: Optional[str] = None
    b64_json: Optional[str] = None

class ChatChoices(BaseModel):
    finish_reason: str
    index: int
    message: ChatContent

class VoiceSegments(BaseModel):
    start: float
    end: float
    content: str


class ChatCompletionRequest(BaseModel):
    provider_model: Optional[str] = None
    messages: List[BaseMessage]
    functions: Optional[List[FunctionCall]] = None


class CompletionRequest(BaseModel):
    provider_model: Optional[str] = None
    prompt: BaseMessage


class EmbeddingsRequest(BaseModel):
    provider_model: str
    embeddings_inputs: List[str]


class ImageRequest(BaseModel):
    provider_model: str
    prompt: str
    size: Literal['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792']
    negative_prompt: Optional[str] = None
    steps: Optional[int] = None
    response_format: Literal['url', 'b64_json'] = "b64_json"
    download_path: Optional[str] = None

class TTSRequest(BaseModel):
    provider_model: str
    text: str
    voice: Optional[str] = None
    target_lang: Optional[str] = 'en'
    response_format: Literal['url', 'b64_json'] = "b64_json"
    download_path: Optional[str] = None

class TranscriptionRequest(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    provider_model: str
    audio: str | np.ndarray
    input_type: Literal["b64_json", "url", "numpy"]
    lang: Optional[str]

class CompletionResponse(BaseModel):
    messages_response: Optional[List[BaseMessage]] = None
    provider_model: Optional[str] = None
    uuid: Optional[str] = None
    object_type: Optional[str] = None
    created: Optional[int] = None
    usage: Optional[Usage] = None
    response: Optional[List[CompletionChoices]] = None


class EmbeddingsResponse(BaseModel):
    embeddings_data: Optional[List[List[float]]] = None
    provider_model: Optional[str] = None
    uuid: Optional[str] = None
    object_type: Optional[str] = None
    created: Optional[int] = None
    response: Optional[List[List[float]]] = None
   

class ChatResponse(BaseModel):
    messages_response: Optional[List[BaseMessage]] = None
    provider_model: Optional[str] = None
    uuid: Optional[str] = None
    object_type: Optional[str] = None
    created: Optional[int] = None
    usage: Optional[Usage] = None
    response: Optional[List[ChatChoices]] = None


class ImageResponse(BaseModel):
    provider_model: Optional[str] = None
    uuid: Optional[str] = None
    created: Optional[int] = None
    response: Optional[List[ImageContent]] = None


class TTSResponse(BaseModel):
    provider_model: Optional[str] = None
    uuid: Optional[str] = None
    gender: Literal["Male", "Female"] = "Male"
    created: Optional[int] = None
    response: Optional[str] = None


class TranscriptionResponse(BaseModel):
    provider_model: str
    uuid: Optional[str] = None
    created: Optional[int] = None
    response: Optional[str] = None
    segments: Optional[List[VoiceSegments]] = None
    lang: Optional[str] = None



class ChatData(ChatResponse, ChatCompletionRequest):
    provider: Optional[str] = None
    configs: Any
    metadata: Dict[str, Any]


class CompletionData(CompletionResponse, CompletionRequest):
    provider: Optional[str] = None
    configs: Any
    metadata: Dict[str, Any]


class EmbeddingsData(EmbeddingsResponse, EmbeddingsRequest):
    provider: Optional[str] = None
    metadata: Dict[str, Any]

class ImageData(ImageResponse, ImageRequest):
    provider: Optional[str] = None
    configs: Any
    metadata: Dict[str, Any]

class TTSData(TTSResponse, TTSRequest):
    provider: Optional[str] = None
    metadata: Dict[str, Any]

class TranscriptionData(TranscriptionResponse, TranscriptionRequest):
    provider: Optional[str] = None
    metadata: Dict[str, Any]
