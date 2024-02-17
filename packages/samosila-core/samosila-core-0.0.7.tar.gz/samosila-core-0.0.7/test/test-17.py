import base64
import time
from dotenv import load_dotenv

from samosila_core import (
    TTSProvider, ElevenLabsProvider,
    CallbackManager, CompleteInput, ManipulationManager, UserMessage
)

load_dotenv()

callback_manager = CallbackManager([])
manipulation_manager = ManipulationManager([])
configs = CompleteInput(provider_model="edge_tts", api_key="")
# configs = CompleteInput(provider_model="tts_models/multilingual/multi-dataset/xtts_v2",
#                         api_key="75dcd92ad4147404c2d7716824ae935a9524cdb15ad42f01038b5c92f0baae92")
# configs = CompleteInput(provider_model="eleven_monolingual_v1", emotion="rPmPG0PDDg4kf0hjjvU0",
#                         api_key="0f7e27f229322340aea39e639dbda7ed")

text = "Born and raised in the charming south, I can add a touch of sweet southern hospitality to your audiobooks and podcasts"

tts = TTSProvider(
    configs, 
    callback_manager, 
    manipulation_manager
)
# tts = ElevenLabsProvider(
#     configs, callback_manager, manipulation_manager)

start = time.time()

res = tts.tts(text)

if res is not None:
  print(time.time() - start)

  decoded_audio = base64.b64decode(res.response or "")
  # decoded_audio = res.response

  # Write the decoded audio data to a new file
  with open('test-3.mp3', 'wb') as decoded_file:
      decoded_file.write(decoded_audio)
