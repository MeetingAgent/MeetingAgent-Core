# Audio Processing
import pyaudio
import wave
import whisper

# GUI 
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.support import install_twisted_reactor
install_twisted_reactor()

# Local
from message_buddy_system.gpt_utils import gpt_4_answer
from message_buddy_system.prompts import MESSAGE_BUDDY_MAIN_PROMPT, EXTRACT_QUERY_PROMPT

def get_audio() -> None:
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    frames = []
    try:
        print("Recording...")
        for i in range(0, int(44100 / 1024 * 20)):  # 20 seconds of audio
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

def whisper_process_audio(audio_file: str) -> str:
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result["text"]

def gpt4_extract_query(input_text: str) -> str:
    print("\n\n\n###### EXTRACTING QUERY FROM TEXT ######\n\n\n")
    messages = [{"role": "system", "content": EXTRACT_QUERY_PROMPT}, {"role": "user", "content": input_text}]
    query = gpt_4_answer(messages=messages)
    print("\n\n\n###### FINISHED EXTRACTING QUERY FROM TEXT ######\n\n\n")
    return query

def meeting_buddy() -> str:
    get_audio()
    input_text = whisper_process_audio("audio_output/audio.wav")
    formatted_input = gpt4_extract_query(input_text)

    messages = [{"role": "system", "content": MESSAGE_BUDDY_MAIN_PROMPT}, {"role": "user", "content": formatted_input}]

    print("\n\n\n###### RESPONDING TO QUERY ######\n\n\n")
    answer = gpt_4_answer(messages=messages)
    print("\n\n\n###### RESPONDED TO QUERY ######\n\n\n")

    return answer

class MeetingBuddyApp(App):
    def build(self):
        self.label = Label(text='', size_hint_y=None, valign='top')
        self.label.bind(size=self.label.setter('text_size'))
        scroll = ScrollView(size_hint=(None, None), size=(400, 400))
        scroll.add_widget(self.label)
        button = Button(text='Start Meeting Buddy', on_release=self.start_meeting_buddy)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(button)
        layout.add_widget(scroll)
        return layout

    def update_label(self, text):
        self.label.text = text

    def start_meeting_buddy(self, instance):
        answer = meeting_buddy()
        self.update_label(answer)

if __name__ == "__main__":
    print("\n\n###### STARTING MEETING BUDDY ######\n\n")
    MeetingBuddyApp().run()