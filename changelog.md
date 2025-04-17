# Changelog

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
