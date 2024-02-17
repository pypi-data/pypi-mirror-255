import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"


tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

wav = tts.tts(text="The Massively Multilingual Speech (MMS) project expands speech technology from about 100 languages to over 1,000 by building a single multilingual speech recognition model supporting over 1,100 languages!",
              speaker_wav="test/3.wav", language="en")

# Text to speech to a file
tts.tts_to_file(text="The Massively Multilingual Speech (MMS) project expands speech technology from about 100 languages to over 1,000 by building a single multilingual speech recognition model supporting over 1,100 languages", speaker_wav="test/3.wav",
                language="en", file_path="output.wav")

# from RealtimeTTS import TextToAudioStream, CoquiEngine

# def dummy_generator():
#     yield "Hey guys! These here are realtime spoken sentences based on local text synthesis. "
#     yield "With a local, neuronal, cloned voice. So every spoken sentence sounds unique."

# import logging
# logging.basicConfig(level=logging.INFO)    
# engine = CoquiEngine(
#   model_name="tts_models/multilingual/multi-dataset/xtts_v2",
#   level=logging.INFO
# )


# stream = TextToAudioStream(engine)

# print ("Starting to play stream")
# stream.feed(dummy_generator()).play(log_synthesized_text=True)

# engine.shutdown()