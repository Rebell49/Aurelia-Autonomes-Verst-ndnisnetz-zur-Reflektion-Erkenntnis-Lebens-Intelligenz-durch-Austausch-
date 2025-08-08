import os
import datetime
import traceback

class ThoughtStream:
    def __init__(self, max_thoughts=100):
        self.thoughts = []
        self.max_thoughts = max_thoughts

    def update(self):
        """
        Fügt bei Bedarf einen neuen Gedanken hinzu.
        """
        try:
            if len(self.thoughts) < self.max_thoughts:
                self.thoughts.append("Neuer Gedanke fließt...")
        except Exception as e:
            self._log_error("Fehler beim Aktualisieren der Gedanken", e)

    def get_recent_thoughts(self, count=10):
        """
        Gibt die letzten 'count' Gedanken zurück.
        """
        try:
            return self.thoughts[-count:]
        except Exception as e:
            self._log_error("Fehler beim Abrufen der letzten Gedanken", e)
            return []

    def _log_error(self, message, exception=None):
        """
        Schreibt Fehler in eine Log-Datei auf der SD-Karte.
        """
        try:
            log_path = os.path.join(
                os.getenv('EXTERNAL_STORAGE', '/sdcard'),
                'aurelia_thought_stream_errors.txt'
            )
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.datetime.now()}] ERROR: {message}\n")
                if exception:
                    f.write(f"{exception}\n")
                    f.write(traceback.format_exc() + "\n")
                f.write("=" * 40 + "\n")
        except Exception as log_err:
            print(f"[AURELIA] Konnte ThoughtStream-Fehler nicht loggen: {log_err}")
