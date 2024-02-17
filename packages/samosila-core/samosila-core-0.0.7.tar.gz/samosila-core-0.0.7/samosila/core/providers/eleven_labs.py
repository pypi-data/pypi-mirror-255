import base64
from typing import Any, Dict, Literal, Optional


from ..types import (
    CallbackManager, Callbacks, ProviderBase, ManipulationManager,
    Manipulations, TTSInput,
    tts_decorator, TTSData
)


class ElevenLabsProvider(ProviderBase):

    def __init__(self, configs: TTSInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate()
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: TTSInput = configs

    @classmethod
    def model_validate(cls):
        pass

    @tts_decorator
    def tts(
        self,
        text: str,
        data: Optional[TTSData] = None,
        gender: Literal["Male", "Female"] = "Male",
        file_name: Optional[str] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ):
        try:
            if data is None:
                raise Exception("Decorator didnt Initialized Data")            
            data = self.tts_generations(data, callbacks)
            return data
        except Exception as e:
            raise e

    def tts_generations(self, data: TTSData, callbacks):
        try:
            import requests

            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.configs.emotion}"
            
            payload = {
                "model_id": data.provider_model,
                "text": data.text,
                "voice_settings": {
                    "similarity_boost": data.metadata.get("similarity_boost") or 0.75,
                    "stability": data.metadata.get("stability") or 0.5,
                    "use_speaker_boost": data.metadata.get("use_speaker_boost") or True
                }
            }
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.configs.api_key
            }

            response = requests.request(
                "POST", url, json=payload, headers=headers)
            res = b""
            for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                      res += chunk
            
            data.response = base64.b64encode(res).decode()
            
            return data
        except Exception as e:
            raise e
