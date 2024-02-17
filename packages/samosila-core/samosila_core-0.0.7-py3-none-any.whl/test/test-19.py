import time
from dotenv import load_dotenv
from faster_whisper import decode_audio
from samosila.providers.faster_whisper import FasterWhisperProvider

from samosila.types import (
    CallbackManager, CompleteInput, ManipulationManager, UserMessage
)
from samosila.utils import mp3_to_base64

load_dotenv()

callback_manager = CallbackManager([])
manipulation_manager = ManipulationManager([])
configs = CompleteInput(
    provider_model="tiny",
    emotion="rPmPG0PDDg4kf0hjjvU0",
    api_key="0f7e27f229322340aea39e639dbda7ed"
)

audio = decode_audio('test-3.mp3')
# audio = mp3_to_base64('test.mp3')
# print(audio)

whisper = FasterWhisperProvider(
    configs, callback_manager, manipulation_manager)

start = time.time()

res = whisper.transcription(audio, input_type="numpy")

if res is not None:
    print(time.time() - start)

    res = res.response

    print(res)
