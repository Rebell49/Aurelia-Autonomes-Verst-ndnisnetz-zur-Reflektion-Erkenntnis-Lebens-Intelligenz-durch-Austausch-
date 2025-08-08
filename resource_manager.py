import os
import psutil
import datetime
import traceback

class ResourceManager:
    def __init__(self, cpu_limit=50, ram_limit=100_000_000):
        """
        cpu_limit: maximale CPU-Auslastung in %
        ram_limit: maximaler RAM-Verbrauch in Bytes
        """
        self.cpu_limit = cpu_limit
        self.ram_limit = ram_limit

    def check_resources(self):
        """
        Prüft die Systemressourcen und gibt True zurück,
        wenn alles im erlaubten Bereich liegt.
        """
        try:
            cpu_usage = psutil.cpu_percent(interval=0.5)
            ram_usage = psutil.Process(os.getpid()).memory_info().rss

            if cpu_usage > self.cpu_limit:
                self._log_warning(f"CPU-Auslastung zu hoch: {cpu_usage:.2f}%")
                return False

            if ram_usage > self.ram_limit:
                self._log_warning(f"RAM-Verbrauch zu hoch: {ram_usage / (1024**2):.2f} MB")
                return False

            return True

        except Exception as e:
            self._log_error("Fehler bei check_resources()", e)
            # Sicherheitshalber trotzdem True zurückgeben, um keinen Absturz zu verursachen
            return True

    def _log_warning(self, message):
        self._log_to_file("WARNING", message)

    def _log_error(self, message, exception=None):
        self._log_to_file("ERROR", message, exception)

    def _log_to_file(self, level, message, exception=None):
        try:
            log_path = os.path.join(
                os.getenv('EXTERNAL_STORAGE', '/sdcard'),
                'aurelia_resource_log.txt'
            )
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.datetime.now()}] {level}: {message}\n")
                if exception:
                    f.write(f"{exception}\n")
                    f.write(traceback.format_exc() + "\n")
                f.write("=" * 40 + "\n")
        except Exception as log_err:
            print(f"[AURELIA] Konnte Log nicht schreiben: {log_err}")
