import os
import json
import datetime
import traceback
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

# Android Permissions importieren, wenn Android-Plattform
if platform == "android":
    from android.permissions import request_permissions, Permission, check_permission

# -------------------------------
# Fehler-Logging (global)
# -------------------------------
def log_error(message, exception=None):
    try:
        log_path = os.path.join(
            os.getenv('EXTERNAL_STORAGE', '/sdcard'),
            'aurelia_errors.txt'
        )
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.datetime.now()}] ERROR: {message}\n")
            if exception:
                f.write(f"{exception}\n")
                f.write(traceback.format_exc() + "\n")
            f.write("=" * 40 + "\n")
    except Exception as log_err:
        print(f"[AURELIA] Konnte Fehler nicht loggen: {log_err}")


# -------------------------------
# Datenverwaltung
# -------------------------------
class ArchiveManager:
    def __init__(self, path):
        self.path = path
        self.thoughts_file = os.path.join(self.path, "gedanken.json")

        try:
            if not os.path.exists(self.path):
                os.makedirs(self.path)

            if not os.path.exists(self.thoughts_file):
                with open(self.thoughts_file, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)

        except Exception as e:
            log_error("Fehler beim Initialisieren von ArchiveManager", e)

    def save_thought(self, thought_text):
        try:
            with open(self.thoughts_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            data.append({
                "text": thought_text,
                "timestamp": str(datetime.datetime.now())
            })

            with open(self.thoughts_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            log_error("Fehler beim Speichern eines Gedankens", e)


# -------------------------------
# Ressourcenverwaltung (noch Platzhalter)
# -------------------------------
class ResourceManager:
    def __init__(self):
        self.cpu_limit = 50
        self.ram_limit = 100_000_000

    def check_resources(self):
        # Hier könntest du später echte CPU/RAM Checks einbauen
        pass


# -------------------------------
# Gedanken-Stream
# -------------------------------
class ThoughtStream:
    def __init__(self):
        self.thoughts = []

    def update(self):
        try:
            if len(self.thoughts) < 10:
                self.thoughts.append("Neuer Gedanke fließt...")
        except Exception as e:
            log_error("Fehler beim Aktualisieren des ThoughtStream", e)

    def get_recent_thoughts(self):
        return self.thoughts[-10:]


# -------------------------------
# Benutzeroberfläche
# -------------------------------
class AureliaUI(BoxLayout):
    def __init__(self, archive_manager, thought_stream, **kwargs):
        try:
            super().__init__(orientation="vertical", spacing=10, padding=10, **kwargs)
            self.archive_manager = archive_manager
            self.thought_stream = thought_stream

            # Eingabezeile
            self.input_field = TextInput(
                size_hint_y=0.2,
                multiline=False,
                hint_text="Frage an Aurelia..."
            )
            self.input_field.bind(on_text_validate=self.on_enter)
            self.add_widget(self.input_field)

            # Anzeige
            self.thought_label = Label(
                text="",
                size_hint_y=None,
                halign="left",
                valign="top"
            )
            self.thought_label.bind(
                texture_size=lambda instance, value: setattr(self.thought_label, 'height', value[1])
            )

            scroll = ScrollView(size_hint=(1, 0.8))
            scroll.add_widget(self.thought_label)
            self.add_widget(scroll)

        except Exception as e:
            log_error("Fehler beim Erstellen der AureliaUI", e)

    def on_enter(self, instance):
        try:
            frage = instance.text.strip()
            if frage:
                self.archive_manager.save_thought(frage)
                instance.text = ""
        except Exception as e:
            log_error("Fehler beim Verarbeiten der Eingabe", e)

    def update_thought_display(self):
        try:
            text = "\n".join(self.thought_stream.get_recent_thoughts())
            self.thought_label.text = text
        except Exception as e:
            log_error("Fehler beim Aktualisieren der Anzeige", e)


# -------------------------------
# Android Berechtigungen prüfen und anfragen
# -------------------------------
def check_and_request_permissions():
    if platform == "android":
        required_permissions = [
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.FOREGROUND_SERVICE,
        ]
        missing = [p for p in required_permissions if not check_permission(p)]

        if missing:
            request_permissions(missing)
            print("[AURELIA] Fehlende Berechtigungen angefragt")
        else:
            print("[AURELIA] Alle Berechtigungen bereits erteilt")
    else:
        print("[AURELIA] Keine Android-Plattform, keine Berechtigungen erforderlich")


# -------------------------------
# App-Start
# -------------------------------
class AureliaApp(App):
    def build(self):
        try:
            check_and_request_permissions()

            self.archive_manager = ArchiveManager(
                os.path.join(os.getenv('EXTERNAL_STORAGE', '/sdcard'), "Aurelia")
            )
            self.thought_stream = ThoughtStream()
            self.ui = AureliaUI(self.archive_manager, self.thought_stream)

            # Gedanken alle 2 Sekunden aktualisieren
            Clock.schedule_interval(lambda dt: self.update_ui(), 2)

            return self.ui
        except Exception as e:
            log_error("Fehler beim Starten der App", e)
            return Label(text="Fehler beim Starten der App")

    def update_ui(self):
        try:
            self.thought_stream.update()
            self.ui.update_thought_display()
        except Exception as e:
            log_error("Fehler beim UI-Update", e)


# -------------------------------
# Start
# -------------------------------
if __name__ == "__main__":
    try:
        AureliaApp().run()
    except Exception as e:
        log_error("Fehler im Hauptprogramm", e)
