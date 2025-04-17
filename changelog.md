# Changelog

## 1.1.0 (2025-04-17)
- Major Release: Push-to-Talk (PTT) ist jetzt vollständig als Hintergrundprozess in den Bot integriert.
- Individuelle Prompts (z.B. aus prompt.txt/.env) werden jetzt auch für PTT-Audio genutzt.
- Die Datei ptt_audio.py wurde entfernt, die gesamte Logik befindet sich nun in ptt.py und wird von main.py aus gestartet.
- Diverse interne Verbesserungen und Refactoring.

## 1.0.2 (2025-04-17)
- Push-to-Talk (PTT) ist jetzt vollständig in den Bot integriert und läuft als Hintergrundprozess.
- Die Datei ptt_audio.py wurde entfernt, die gesamte Logik befindet sich nun in ptt.py und wird von main.py aus gestartet.
- Sprachaufnahmen werden weiterhin per Maus5 getriggert, aber direkt im Kontext des Bots verarbeitet.

## 1.0.1 (2025-04-17)
- Der Bot reagiert jetzt ausschließlich auf Nachrichten mit @Nicole. Die Unterstützung für /Nicole als Trigger wurde entfernt, da Twitch Nachrichten mit / als fehlerhafte Befehle behandelt.

## 1.0.0 (2025-04-17)
- **Release 1.0.0:** Siehe nachfolgende Einträge für alle enthaltenen Features und Bugfixes.

## 2025-04-17
- Die Anzahl der generierten Token ist jetzt einstellbar, default sind nun 500.
- Lange Antworten der KI-Schnittstelle werden nun aufgeteilt.
- Antworten werden jetzt bei der Ausgabe im Chat nur noch an Wortgrenzen getrennt, nicht mehr mitten im Wort (event_message in main.py angepasst, Hilfsfunktion split_text_on_word_boundary hinzugefügt).
- Fehlerbehebung: Die Länge des ersten Antwort-Blocks (inkl. Prefix) überschreitet nicht mehr das 500-Zeichen-Limit von TwitchIO. Die Blockaufteilung wurde entsprechend angepasst.

## 2025-04-17 (Timeout & TTS-Verbesserungen)
- Timeout für ElevenLabs-TTS-API in main.py von 15s auf 60s erhöht, um längere Texte zu unterstützen.
- Explizite Fehlerbehandlung für Timeout ergänzt: Nutzer erhalten nun einen klaren Hinweis, wenn das Timeout überschritten wird.
- Docstring der speak_text-Methode nach Google-Style erweitert und Hinweise zu Textlänge/Timeout ergänzt.
- Hinweise zu langen Texten und Timeout-Verhalten in README.md und README_de.md ergänzt.

## 2025-04-16
- Bot reagiert jetzt auf Nachrichten mit '@Nicole' im Chat und antwortet entsprechend.
- Neuer Testfall für die Nicole-Erkennung in test_main.py hinzugefügt.
- Changelog-Datei erstellt und gepflegt.
