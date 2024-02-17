import onnxruntime
import soundfile as sf
import yaml

from ttstokenizer import TTSTokenizer

# This example assumes the files have been downloaded locally
with open("ljspeech-jets-onnx/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Create model
model = onnxruntime.InferenceSession(
    "ljspeech-jets-onnx/model.onnx",
    providers=["CPUExecutionProvider"]
)

# Create tokenizer
tokenizer = TTSTokenizer(config["token"]["list"])

# Tokenize inputs
inputs = tokenizer("Say something here")

# Generate speech
outputs = model.run(None, {"text": inputs})

# Write to file
sf.write("out.wav", outputs[0], 22050)
