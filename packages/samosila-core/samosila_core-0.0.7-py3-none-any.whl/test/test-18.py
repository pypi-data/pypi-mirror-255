import time
import torch
from faster_whisper import WhisperModel

# model_size = "large-v3"
model_size = "tiny"

start = time.time()

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)

# Run on GPU with FP16
model = WhisperModel(
    model_size_or_path=model_size,
    device=device,
    compute_type="int8"
)
# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, info = model.transcribe("test-2.mp3", beam_size=5)

print("Detected language '%s' with probability %f" %
      (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

print(time.time() - start)