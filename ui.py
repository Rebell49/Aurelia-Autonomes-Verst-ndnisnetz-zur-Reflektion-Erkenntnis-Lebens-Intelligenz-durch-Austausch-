import os
import datetime
import traceback
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView


class AureliaUI(BoxLayout):
    def __init__(self, archive_manager, thought_stream, **kwargs):
        try:
            super().__init__(orientation="vertical", spacing=10, padding=10, **kwargs)
            self.archive_manager = archive_manager
            self.thought_stream = thought_stream

            # Eingabefeld
            self.input_field = TextInput(
                size_hint_y=0.2,
                multiline=False,
                hint_text="Frage an Aurelia..."
            )
            self.input_field.bind(on_text_validate=self.on_enter)
            self.add_widget(self.input_field)

            # Scrollbarer Gedankenbereich
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
            self._log_error("Fehler beim Initialisieren der AureliaUI", e)

    def on_enter(self, instance):
        try:
            frage = instance.text.strip()
            if frage:
                self.archive_manager.save_thought(frage)
                instance.text = ""
        except Exception as e:
            self._log_error("Fehler beim Verarbeiten der Eingabe", e)

    def update_thought_display(self):
        try:
            text = "\n".join(self.thought_stream.get_recent_thoughts())
            self.thought_label.text = text
        except Exception as e:
            self._log_error("Fehler beim Aktualisieren der Anzeige", e)

    def _log_error(self, message, exception=None):
        """
        Schreibt Fehler in eine Log-Datei auf der SD-Karte.
        """
        try:
            log_path = os.path.join(
                os.getenv('EXTERNAL_STORAGE', '/sdcard'),
                'aurelia_ui_errors.txt'
            )
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.datetime.now()}] ERROR: {message}\n")
                if exception:
                    f.write(f"{exception}\n")
                    f.write(traceback.format_exc() + "\n")
                f.write("=" * 40 + "\n")
        except Exception as log_err:
            print(f"[AURELIA UI] Konnte UI-Fehler nicht loggen: {log_err}")
