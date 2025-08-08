import os
import json
import datetime
import traceback

class ArchiveManager:
    def __init__(self, path):
        self.path = path

        # Android-Kompatibilität: sicherstellen, dass der Pfad beschreibbar ist
        if not os.path.exists(self.path):
            try:
                os.makedirs(self.path)
            except Exception as e:
                self._log_error("Konnte Archiv-Verzeichnis nicht erstellen", e)

        self.thoughts_file = os.path.join(self.path, "gedanken.json")

        # Datei anlegen, falls sie nicht existiert oder fehlerhaft ist
        if not os.path.exists(self.thoughts_file):
            self._init_thoughts_file()
        else:
            if not self._is_valid_json(self.thoughts_file):
                self._log_error("Ungültige JSON-Struktur, Datei wird neu erstellt")
                self._init_thoughts_file()

    def _init_thoughts_file(self):
        """Leere Gedankenliste anlegen."""
        try:
            with open(self.thoughts_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._log_error("Fehler beim Erstellen von gedanken.json", e)

    def _is_valid_json(self, filepath):
        """Prüft, ob die Datei gültiges JSON enthält."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                json.load(f)
            return True
        except Exception:
            return False

    def save_thought(self, thought_text):
        """Speichert einen neuen Gedanken in der JSON-Datei."""
        try:
            with open(self.thoughts_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            data.append({
                "text": thought_text,
                "timestamp": datetime.datetime.now().isoformat()
            })

            with open(self.thoughts_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self._log_error("Fehler beim Speichern eines Gedankens", e)

    def _log_error(self, message, exception=None):
        """Schreibt einen Fehlerbericht auf die SD-Karte."""
        try:
            crash_path = os.path.join(
                os.getenv('EXTERNAL_STORAGE', '/sdcard'),
                'aurelia_archive_errors.txt'
            )
            with open(crash_path, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.datetime.now()}] {message}\n")
                if exception:
                    f.write(f"{exception}\n")
                    f.write(traceback.format_exc() + "\n")
                f.write("=" * 40 + "\n")
        except Exception as log_err:
            print(f"[AURELIA] Konnte Fehler nicht loggen: {log_err}")
