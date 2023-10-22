# Audio Processing
import pyaudio
import wave
import whisper
import threading
import time

# GUI 
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.switch import Switch
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.textinput import TextInput 
from kivy.core.window import Window
from kivy.support import install_twisted_reactor
install_twisted_reactor()

# text to speech
from gtts import gTTS
from pydub import AudioSegment
import pygame
from ftlangdetect import detect

# Local
from meeting_buddy_system.gpt_utils import gpt_4_answer, gpt_3_5_turbo_16k_answer
from meeting_buddy_system.prompts import MEETING_BUDDY_MAIN_PROMPT, EXTRACT_QUERY_PROMPT

recording = False 
audio_thread = None 

def get_audio() -> None:
    global recording
    recording = True
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    frames = []
    try:
        print("Recording...")
        while recording: 
            data = stream.read(1024)
            frames.append(data)
        print("Finished recording.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    wf = wave.open('audio_output/audio.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()

def stop_audio() -> None:
    global recording
    recording = False

def whisper_process_audio(audio_file: str) -> str:
    model = whisper.load_model("base") # for multilingual
    result = model.transcribe(audio_file)
    return result["text"]

def detect_language(text: str) -> str:
    cleaned_text = text.replace('\n', ' ')
    return detect(text=cleaned_text, low_memory=True)

def text_to_speech(text: str, output_file='audio_output/output.mp3') -> None:
    language = detect_language(text=text)["lang"]
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(output_file)
    print(f'Audio saved as {output_file}')

# initialize mixer
pygame.mixer.init()

def play_audio(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def stop_audio_playback():
    pygame.mixer.music.stop()

def gpt_pipeline(meeting_context: str, input_text: str) -> str:
    """
    Extract query from text and produce the final answer to query.
    """

    print("\n\n\n###### EXTRACTING QUERY FROM TEXT ######\n\n\n")
    messages = [{"role": "system", "content": EXTRACT_QUERY_PROMPT}, {"role": "user", "content": input_text}]
    query = gpt_3_5_turbo_16k_answer(messages=messages)
    full_query_text = f"Extracted Query: {query}"
    print("\n\n\n###### FINISHED EXTRACTING QUERY FROM TEXT ######\n\n\n")

    print("\n\n\n###### RESPONDING TO QUERY ######\n\n\n")
    messages = [{"role": "system", "content": MEETING_BUDDY_MAIN_PROMPT.format(meeting_context=meeting_context)}, {"role": "user", "content": query}]
    answer = gpt_4_answer(messages=messages)
    full_answer_text = f"Answer: {answer}"
    print("\n\n\n###### RESPONDED TO QUERY ######\n\n\n")

    aggregated_text = full_query_text + "\n\n" + full_answer_text

    if app.tts_switch.active:
        # getting text to speech response
        text_to_speech(answer)
        Clock.schedule_once(lambda dt: app.update_answer_text(aggregated_text))
        play_audio('audio_output/output.mp3')

    else:
        # Update the answer text without text-to-speech
        Clock.schedule_once(lambda dt: app.update_answer_text(aggregated_text))

    return query, answer

def meeting_buddy(meeting_context: str) -> None: 
    global audio_thread  
    audio_thread = threading.Thread(target=get_audio)
    audio_thread.start()
    audio_thread.join() 

    input_text = whisper_process_audio("audio_output/audio.wav")
    question, answer = gpt_pipeline(meeting_context=meeting_context, input_text=input_text)

    print(f"Question: {question}")
    print(f"Answer: {answer}")

Window.size = (800, 600)

class MeetingBuddyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audio_thread = None
        self.context_input = TextInput(
            hint_text='Paste your meeting notes here',
            multiline=True,
            size_hint=(1, 0.2),
            font_size='20sp',
            background_color=[0, 0, 0, 1],
            foreground_color=[1, 1, 1, 1]
        )

    def build(self):
        self.answer_output = TextInput(
            text='',
            multiline=True,
            size_hint=(1, 0.6),
            font_size='20sp',
            readonly=True,
            background_color=[0, 0, 0, 1],
            foreground_color=[1, 1, 1, 1]
        )

        start_button = Button(
            text='Start Recording',
            on_release=self.start_meeting_buddy,
            size_hint=(1, 0.1),
            font_size='20sp'
        )

        stop_button_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.3))

        stop_button = Button(
            text='Stop Recording',
            on_release=self.stop_recording,
            size_hint=(1, 0.1),
            font_size='20sp'
        )

        switch_layout = BoxLayout(
            orientation='horizontal',
            spacing=10, 
            size_hint=(None, None),
            size=(200, 175), 
            pos_hint={'center_x': 0.5}
        )

        tts_label = Label(
            text='Text to Speech:',
            size_hint=(None, None),
            size=(0, 200)
        )
    
        self.tts_switch = Switch(size_hint=(None, None), size=(400, 200))

        switch_layout.add_widget(tts_label)
        switch_layout.add_widget(self.tts_switch)

        stop_button_layout.add_widget(stop_button)
        stop_button_layout.add_widget(switch_layout)

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        layout.add_widget(self.context_input)
        layout.add_widget(start_button)
        layout.add_widget(stop_button_layout) 
        layout.add_widget(self.answer_output)

        return layout
    
    def update_answer_text(self, text):
        self.answer_output.text = f'{text}'

    def start_meeting_buddy(self, instance):
        global app 
        app = self 
        meeting_context = self.context_input.text 
        global audio_thread  
        audio_thread = threading.Thread(target=meeting_buddy, args=(meeting_context,))
        audio_thread.start() 

        stop_audio_playback()

    def stop_recording(self, instance):
        stop_audio()
        if self.audio_thread is not None:
            self.audio_thread.join()

        Clock.schedule_once(self.delayed_update, 1)

    def delayed_update(self, dt):
        self.update_answer_text("Getting answer...")

if __name__ == "__main__":
    print("\n\n###### STARTING MEETING BUDDY ######\n\n")
    MeetingBuddyApp().run()