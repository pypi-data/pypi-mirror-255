import asyncio
import base64
import random

import edge_tts
from edge_tts import VoicesManager, list_voices

TEXT = "Hello World!"
VOICE = "en-GB-SoniaNeural"
OUTPUT_FILE = "test.mp3"


async def amain() -> None:
    """Main function"""
            
    # voices = await list_voices()
    # print(voices)
    voices = await VoicesManager.create()
    voice = voices.find(Gender= "Male", Language="en")

    mp3 = b''
    communicate = edge_tts.Communicate(TEXT, random.choice(voice)["Name"])
    # await communicate.save("output.wav")
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3 += chunk["data"]
    print(mp3)

if __name__ == "__main__":
    with open('test.mp3', 'rb') as audio_file:
        # Read the file content
        audio_data = audio_file.read()

    # Encode the audio data to base64
    encoded_audio = base64.b64encode(audio_data)

    # Decode the base64 data
    decoded_audio = base64.b64decode(encoded_audio)

    # Write the decoded audio data to a new file
    with open('decoded_test.mp3', 'wb') as decoded_file:
        decoded_file.write(decoded_audio)
    # loop = asyncio.get_event_loop_policy().get_event_loop()
    # try:
    #     loop.run_until_complete(amain())
    # finally:
    #     loop.close()