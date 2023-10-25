import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

config = XttsConfig()
config.load_json("/Users/andre/Documents/projects/Meeting-Buddy/voice_cloning/XTTS-v1/config.json")

model = Xtts.init_from_config(config)

checkpoint_dir = "/Users/andre/Documents/projects/Meeting-Buddy/voice_cloning/XTTS-v1"
model.load_checkpoint(config, checkpoint_dir=checkpoint_dir, eval=True)

if torch.cuda.is_available():
    model.cuda()

outputs = model.synthesize(
    "It took me quite a long time to develop a voice and now that I have it I am not going to be silent.",
    config,
    speaker_wav="/Users/andre/Documents/projects/Meeting-Buddy/voice_cloning/audio_samples/default_audio.wav",
    gpt_cond_len=3,
    language="en",
)
