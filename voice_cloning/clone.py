import torch
from TTS.api import TTS
import glob

class MyTTS:
    def __init__(self):
        # Get device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
        self.use_default_speaker = False
        self.speaker_wav = self._get_speaker()

    def _get_speaker(self):
        # speaker audio file
        wav_files = glob.glob("voice_cloning/audio_samples/*.wav")
        print("WAV FILES: ", wav_files)
        if wav_files:
            if self.use_default_speaker:
                wav_file = "voice_cloning/audio_samples/default_audio.wav"
            else: 
                wav_file = wav_files[0] if wav_files[0] != "default_audio.wav" else FileNotFoundError("Add your audio.wav to /voice_cloning/audio_samples")

        print("WAV FILE: ", wav_file)
        return wav_file

    def text_to_speech(self, text, output_file):
        self.tts.tts_with_vc_to_file(
            text,
            speaker_wav=self.speaker_wav,
            file_path=output_file
        )