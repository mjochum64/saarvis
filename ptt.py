import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import mouse
import threading
import time
import requests
import tempfile
import os
from ai_responder import AIResponder

class PTTRecorder:
    def __init__(self):
        self.recording = False
        self.frames = []
        self.stream = None
        self.lock = threading.Lock()

    def _callback(self, indata, frames, time_info, status):
        if self.recording:
            with self.lock:
                self.frames.append(indata.copy())

    def start_recording(self):
        if not self.recording:
            print("Aufnahme gestartet...")
            self.frames = []
            self.stream = sd.InputStream(
                samplerate=16000,
                channels=1,
                callback=self._callback
            )
            self.stream.start()
            self.recording = True

    def stop_recording(self, filename="aufnahme.wav"):
        if self.recording:
            print(f"Aufnahme gestoppt. Speichere nach {filename}")
            self.recording = False
            self.stream.stop()
            self.stream.close()
            audio = np.concatenate(self.frames, axis=0)
            wav.write(filename, 16000, audio)
            print(f"Datei gespeichert: {filename}")
            self.handle_transcription_and_ai(filename)

    def handle_transcription_and_ai(self, filename):
        try:
            from openai import OpenAI
        except ImportError:
            print("Fehlende Abhängigkeit: openai. Bitte installiere mit 'pip install openai'.")
            return
        api_key = os.environ.get("OPENAI_API_KEY")
        model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        system_prompt = os.environ.get('OPENAI_SYSTEM_PROMPT', 'Du bist ein hilfreicher, freundlicher Chatbot für Twitch.').replace('\\n', '\n')
        system_prompt_file = os.environ.get('OPENAI_SYSTEM_PROMPT_FILE')
        print("Transkribiere Audio mit Whisper...")
        client = OpenAI(api_key=api_key)
        with open(filename, "rb") as audio_file:
            try:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            except Exception as e:
                print(f"Fehler bei der Transkription: {e}")
                return
        print(f"Transkript: {transcript}")
        print("Sende an KI...")
        ai = AIResponder(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            system_prompt_file=system_prompt_file
        )
        try:
            response = ai.get_response(transcript)
        except Exception as e:
            print(f"Fehler bei der KI-Anfrage: {e}")
            return
        print("KI-Antwort:")
        max_total_length = 500
        blocks = self.split_text_on_word_boundary(response, max_total_length)
        for block in blocks:
            print(block)
            self.speak_text(block)

    @staticmethod
    def split_text_on_word_boundary(text: str, max_length: int):
        words = text.split()
        blocks = []
        current_block = ''
        for word in words:
            if current_block:
                if len(current_block) + 1 + len(word) > max_length:
                    blocks.append(current_block)
                    current_block = word
                else:
                    current_block += ' ' + word
            else:
                if len(word) > max_length:
                    blocks.append(word[:max_length])
                    current_block = word[max_length:]
                else:
                    current_block = word
        if current_block:
            blocks.append(current_block)
        return blocks

    def speak_text(self, text: str):
        api_key = os.environ.get('ELEVENLABS_API_KEY', 'PLACEHOLDER_API_KEY')
        voice_id = os.environ.get('ELEVENLABS_VOICE_ID', 'tKmESGVo91DcC5kFPRS6')
        model_id = os.environ.get('ELEVENLABS_MODEL_ID', 'eleven_multilingual_v2')
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {"stability": 0.75, "similarity_boost": 0.25}
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file.write(response.content)
                tmp_file.flush()
                try:
                    import subprocess
                    subprocess.run(["mpg123", "-q", tmp_file.name], check=True)
                except Exception:
                    try:
                        subprocess.run(["mpv", "--quiet", tmp_file.name], check=True)
                    except Exception as e:
                        print(f"Audioausgabe fehlgeschlagen: {e}")
                finally:
                    try:
                        os.remove(tmp_file.name)
                    except Exception:
                        pass
        except Exception as exc:
            print(f"TTS-Fehler: {exc}")

def ptt_listener_background():
    recorder = PTTRecorder()
    def on_click(x, y, button, pressed):
        SUPPORTED_BUTTONS = (mouse.Button.button9,)
        if button in SUPPORTED_BUTTONS:
            if pressed:
                recorder.start_recording()
            else:
                recorder.stop_recording()
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    print("PTT-Listener im Hintergrund gestartet (Maus5 für Aufnahme)")
    return listener
