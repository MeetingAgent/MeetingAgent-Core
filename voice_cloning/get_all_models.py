import torch
from TTS.api import TTS

# List available TTS models
print(TTS().list_models())