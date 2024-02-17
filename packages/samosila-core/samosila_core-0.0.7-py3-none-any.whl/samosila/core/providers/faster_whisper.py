import numpy as np
from typing import Any, Dict, Literal, Optional

from ..utils import base64_to_numpy
from ..types import (
    CallbackManager, Callbacks, ProviderBase, ManipulationManager, VoiceSegments,
    Manipulations, TranscriptionData, FasterWhisperInput, transcription_decorator
)


class FasterWhisperProvider(ProviderBase):

    def __init__(self, configs: FasterWhisperInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate()
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: FasterWhisperInput = configs

    @classmethod
    def model_validate(cls):
        try:
            import torch
            import faster_whisper
        except ImportError:
            raise ImportError(
                "Could not import faster_whisper, torch python package. "
                "Please install it with `pip install faster_whisper`."
            )

        cls.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        cls.model = None

    @transcription_decorator
    def transcription(
        self,
        audio: str | np.ndarray,
        data: Optional[TranscriptionData] = None,
        input_type: Literal["b64_json", "url", "numpy"] = "b64_json",
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ):
        try:
            if data is None:
                raise Exception("Decorator didnt Initialized Data")
            data = self.transcription_generations(data, callbacks)
            return data
        except Exception as e:
            raise e

    def transcription_generations(self, data: TranscriptionData, callbacks):
        try:
            from faster_whisper import WhisperModel

            if self.model is None:
                self.model = WhisperModel(
                    model_size_or_path=data.provider_model,
                    device=self.device,
                    compute_type=data.metadata.get(
                        "compute_type") or "int8"
                )

            if data.input_type == "b64_json" and isinstance(data.audio, str):
                data.audio = base64_to_numpy(data.audio)

            segments, info = self.model.transcribe(data.audio, beam_size=5)

            data.lang = info.language
            data.metadata["duration"] = info.duration
            data.metadata["language_probability"] = info.language_probability

            data.response = ""
            data.segments = []
            for segment in segments:
                data.response += segment.text
                data.segments.append(VoiceSegments(
                    content=segment.text, start=segment.start, end=segment.end))

            return data
        except Exception as e:
            raise e
