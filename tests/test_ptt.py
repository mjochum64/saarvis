import pytest
import time
from ptt import PTTRecorder

def test_ptt_queue_single_transcript():
    """Testet, dass ein einzelnes Transkript korrekt verarbeitet wird."""
    results = []
    def callback(text):
        results.append(text)
    recorder = PTTRecorder(send_chat_callback=callback)
    # Simuliere das direkte Einfügen eines Transkripts (ohne Audio)
    recorder.transcript_queue.put("Test-Transkript 1")
    # Warte kurz, damit der Worker-Thread arbeiten kann
    time.sleep(0.1)
    assert results == ["Test-Transkript 1"]

def test_ptt_queue_multiple_transcripts():
    """Testet, dass mehrere Transkripte in der richtigen Reihenfolge verarbeitet werden."""
    results = []
    def callback(text):
        results.append(text)
    recorder = PTTRecorder(send_chat_callback=callback)
    recorder.transcript_queue.put("Transkript A")
    recorder.transcript_queue.put("Transkript B")
    recorder.transcript_queue.put("Transkript C")
    time.sleep(0.2)
    assert results == ["Transkript A", "Transkript B", "Transkript C"]

def test_ptt_queue_callback_exception():
    """Testet, dass eine Exception im Callback den Worker nicht stoppt."""
    results = []
    def callback(text):
        if text == "fail":
            raise ValueError("Absichtlicher Fehler")
        results.append(text)
    recorder = PTTRecorder(send_chat_callback=callback)
    recorder.transcript_queue.put("ok1")
    recorder.transcript_queue.put("fail")
    recorder.transcript_queue.put("ok2")
    time.sleep(0.2)
    assert "ok1" in results and "ok2" in results
    assert len(results) == 2

def test_context_memory_limit(monkeypatch):
    """Testet, dass die Kontextliste nicht länger als context_size wird."""
    results = []
    recorder = PTTRecorder(send_chat_callback=results.append, context_size=3)
    for i in range(6):
        recorder.transcript_queue.put(f"Transkript {i}")
    time.sleep(0.2)
    # Die letzten 3 Transkripte müssen im Kontext sein
    for idx, call in enumerate(results[-3:], start=3):
        assert f"Transkript {idx}" in call
    # Kontext nie länger als 3
    for call in results:
        assert call.count("Transkript") <= 3

def test_context_env(monkeypatch):
    """Testet, dass die Kontextgröße aus der Umgebungsvariable gelesen wird."""
    monkeypatch.setenv("PTT_CONTEXT_SIZE", "2")
    results = []
    recorder = PTTRecorder(send_chat_callback=results.append)
    recorder.transcript_queue.put("A")
    recorder.transcript_queue.put("B")
    recorder.transcript_queue.put("C")
    time.sleep(0.2)
    # Kontextgröße ist 2, also dürfen maximal 2 Zeilen im Kontext stehen
    for call in results:
        assert call.count("\n") <= 1

def test_context_prompt_building():
    """Testet, dass der Kontext korrekt als Prompt zusammengebaut wird."""
    results = []
    recorder = PTTRecorder(send_chat_callback=results.append, context_size=2)
    recorder.transcript_queue.put("Tobi liebt Schokolade.")
    recorder.transcript_queue.put("Was liebt Tobi?")
    time.sleep(0.1)
    # Die zweite Anfrage sollte den Kontext enthalten
    assert any("Tobi liebt Schokolade." in call and "Was liebt Tobi?" in call for call in results)
