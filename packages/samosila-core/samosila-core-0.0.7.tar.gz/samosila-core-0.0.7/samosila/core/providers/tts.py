import asyncio
import base64
import random
from typing import Any, Dict, Literal, Optional


from ..types import (
    CallbackManager, Callbacks, ProviderBase, ManipulationManager,
    Manipulations, TTSInput,
    tts_decorator, TTSData
)


class TTSProvider(ProviderBase):

    def __init__(self, configs: TTSInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate(configs)
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: TTSInput = configs

    @classmethod
    def model_validate(cls, configs: TTSInput):
        try:
            from TTS.api import TTS
            import edge_tts
            import torch
        except ImportError:
            raise ImportError(
                "Could not import TTS, edge_tts, torch python package. "
                "Please install it with `pip install edge_tts TTS`."
            )
        cls.device = "cuda" if torch.cuda.is_available() else "cpu"
        cls.api = None
        # cls.tts = TTS(configs.provider_model).to(cls.device)

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
            if data.provider_model == "edge_tts":
                loop = asyncio.get_event_loop()
                data = loop.run_until_complete(
                    self.edge_tts_generations(data, callbacks))
            else:
                data = self.tts_generations(data, callbacks)
            return data
        except Exception as e:
            raise e

    async def edge_tts_generations(self, data: TTSData, callbacks):
        try:
            from edge_tts import VoicesManager
            import edge_tts

            voices = await VoicesManager.create()
            voice = voices.find(Gender=data.gender, Language=data.target_lang)

            communicate = edge_tts.Communicate(
                data.text, random.choice(voice)["Name"])
            if data.response_format == "b64_json":
                mp3 = b''
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        if isinstance(chunk["data"], str):
                            chunk["data"] = chunk["data"].encode()
                        mp3 += chunk["data"]
                encoded_audio = base64.b64encode(mp3)

                data.response = encoded_audio.decode()

            return data
        except Exception as e:
            raise e

    def tts_generations(self, data: TTSData, callbacks):
        try:
            from TTS.api import TTS

            if self.api is None:
                self.api = TTS(self.configs.provider_model).to(self.device)
            
            wav = self.api.tts(text=data.text, language=data.target_lang or "en",
                               emotion=self.configs.emotion or "Neutral", speaker="")

            data.response = "".join(t.__str__() for t in wav)

            return data
        except Exception as e:
            raise e
