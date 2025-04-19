import threading
import os
from typing import Any, List, Callable, Optional
import tempfile
import logging
import queue
from pynput import mouse
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests

logging.basicConfig(level=logging.INFO)

class PTTRecorder:
    """Handles Push-to-Talk recording, transcription, AI response, TTS playback, and chat output.

    Args:
        send_chat_callback (Optional[Callable[[str], None]]):
            Callback to send text to chat. Should accept a string (the message block).
        context_size (int): Number of transcripts to keep in memory for context.
    """
    def __init__(self, send_chat_callback: Optional[Callable[[str], None]] = None, context_size: int = None) -> None:
        self.recording: bool = False
        self.frames: list[np.ndarray] = []
        self.stream: Any = None
        self.lock: threading.Lock = threading.Lock()
        self.send_chat_callback = send_chat_callback
        self.transcript_queue: queue.Queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._process_queue_worker, daemon=True)
        self.worker_thread.start()
        # Kontextgröße aus .env lesen, fallback auf 5
        if context_size is None:
            try:
                context_size = int(os.environ.get("PTT_CONTEXT_SIZE", 5))
            except ValueError:
                context_size = 5
        self.context_memory: list[str] = []
        self.context_size = context_size

    def _process_queue_worker(self):
        while True:
            transcript = self.transcript_queue.get()
            # Update context
            self.context_memory.append(transcript)
            if len(self.context_memory) > self.context_size:
                self.context_memory.pop(0)
            # Build prompt: Kontext als Hintergrund, letzte Frage explizit hervorheben
            if len(self.context_memory) > 1:
                context_prompt = "\n".join(self.context_memory[:-1])
                full_prompt = (
                    "Vorherige Konversation (nur als Kontext, nicht beantworten):\n"
                    f"{context_prompt}\n\n"
                    "Letzte Frage (bitte nur diese beantworten):\n"
                    f"{self.context_memory[-1]}"
                )
            else:
                full_prompt = self.context_memory[-1]
            if self.send_chat_callback:
                try:
                    self.send_chat_callback(full_prompt)
                except (ValueError, RuntimeError) as exc:
                    logging.error("Fehler beim Senden in die zentrale Bot-Logik: %s", exc)
            self.transcript_queue.task_done()

    def _callback(self, indata: np.ndarray, _frames: int, _time_info: Any, _status: Any) -> None:
        """Callback for sounddevice InputStream. Appends audio frames if recording."""
        if self.recording:
            with self.lock:
                self.frames.append(indata.copy())

    def start_recording(self) -> None:
        """Start audio recording using sounddevice InputStream."""
        if not self.recording:
            logging.info("Aufnahme gestartet...")
            self.frames = []
            self.stream = sd.InputStream(
                samplerate=16000,
                channels=1,
                callback=self._callback
            )
            self.stream.start()
            self.recording = True

    def stop_recording(self, filename: str = "aufnahme.wav") -> None:
        """Stop recording, save audio to file, and process transcription and AI response.

        Args:
            filename (str): Path to save the recorded WAV file.
        """
        if self.recording:
            logging.info("Aufnahme gestoppt. Speichere nach %s", filename)
            self.recording = False
            self.stream.stop()
            self.stream.close()
            audio = np.concatenate(self.frames, axis=0)
            wav.write(filename, 16000, audio)
            logging.info("Datei gespeichert: %s", filename)
            self.handle_transcription_and_ai(filename)

    def handle_transcription_and_ai(self, filename: str) -> None:
        """Transcribes audio file, gets AI response, and triggers central message processing.

        Args:
            filename (str): Path to the WAV file to transcribe.
        """
        try:
            from openai import OpenAI
        except ImportError:
            logging.error("Fehlende Abhängigkeit: openai. Bitte installiere mit 'pip install openai'.")
            return
        api_key = os.environ.get("OPENAI_API_KEY")
        logging.info("Transkribiere Audio mit Whisper...")
        client = OpenAI(api_key=api_key)
        with open(filename, "rb") as audio_file:
            try:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            except Exception as exc:
                logging.error("Fehler bei der Transkription: %s", exc)
                return
        logging.info("Transkript: %s", transcript)
        logging.info("Lege Transkript in die Warteschlange...")
        self.transcript_queue.put(transcript)

    @staticmethod
    def split_text_on_word_boundary(text: str, max_length: int) -> List[str]:
        """Splits text into blocks of up to max_length characters, breaking only at word boundaries.

        Args:
            text (str): The text to split.
            max_length (int): Maximum length of each block.

        Returns:
            List[str]: List of text blocks, each not exceeding max_length and not splitting words.
        """
        words = text.split()
        blocks: List[str] = []
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

    def speak_text(self, text: str) -> None:
        """Converts text to speech using the ElevenLabs API and plays the resulting audio file.

        Args:
            text (str): The text to be spoken.
        """
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
                except FileNotFoundError:
                    try:
                        subprocess.run(["mpv", "--quiet", tmp_file.name], check=True)
                    except FileNotFoundError as exc2:
                        logging.error("Audioausgabe fehlgeschlagen: %s", exc2)
                finally:
                    try:
                        os.remove(tmp_file.name)
                    except Exception as exc3:
                        logging.warning("Konnte TTS-Audiodatei nicht löschen: %s", exc3)
        except (requests.exceptions.RequestException, subprocess.SubprocessError) as exc:
            logging.error("TTS-Fehler: %s", exc)

def ptt_listener_background(send_chat_callback: Optional[Callable[[str], None]] = None) -> mouse.Listener:
    """Starts a background listener for Push-to-Talk (Mouse5) and returns the listener object.

    Args:
        send_chat_callback (Optional[Callable[[str], None]]): Callback to send text to chat.
    """
    recorder = PTTRecorder(send_chat_callback=send_chat_callback)
    def on_click(x: float, y: float, button: Any, pressed: bool) -> None:
        SUPPORTED_BUTTONS = (mouse.Button.button9,)
        if button in SUPPORTED_BUTTONS:
            logging.info(f"Mouse event: button={button}, pressed={pressed}, x={x}, y={y}")
            if pressed:
                recorder.start_recording()
            else:
                recorder.stop_recording()
        else:
            logging.debug(f"Ignored mouse event: button={button}, pressed={pressed}, x={x}, y={y}")
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    logging.info("PTT-Listener im Hintergrund gestartet (Maus5 für Aufnahme)")
    return listener
