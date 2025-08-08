import os
import json
import traceback
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock

from ui import AureliaUI
from archive_manager import ArchiveManager
from resource_manager import ResourceManager
from thought_stream import ThoughtStream

CONFIG_PATH = "config.json"


def write_crash(exc_info):
    """Schreibt Crash-Informationen in eine Datei auf dem Gerät."""
    try:
        path = os.path.join(
            os.getenv('EXTERNAL_STORAGE', '/sdcard'),
            'aurelia_crash.txt'
        )
        with open(path, 'w', encoding='utf-8') as f:
            f.write("Aurelia Crash Report\n")
            f.write("=" * 40 + "\n\n")
            traceback.print_exception(*exc_info, file=f)
        print(f"[AURELIA] Crash-Log gespeichert unter: {path}")
    except Exception as e:
        print(f"[AURELIA] Konnte Crash-Log nicht schreiben: {e}")


class PermissionPopup(Popup):
    def __init__(self, accept_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Erlaubnis erfragen"
        self.size_hint = (0.8, 0.5)
        self.accept_callback = accept_callback
        self.content = FileChooserListView(
            path=os.path.expanduser("~"),
            filters=["*/"],
            dirselect=True
        )
        self.content.bind(on_submit=self.on_select)

    def on_select(self, chooser, selection, touch):
        if selection:
            self.dismiss()
            self.accept_callback(selection[0])


class AureliaApp(App):
    def build(self):
        try:
            self.load_config()
            self.root = BoxLayout()
            if not self.config.get("archive_path"):
                self.permission_popup = PermissionPopup(self.on_archive_selected)
                self.permission_popup.open()
            else:
                self.start_aurelia(self.config["archive_path"])
            return self.root
        except Exception:
            write_crash(sys.exc_info())
            raise

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def save_config(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f)

    def on_archive_selected(self, path):
        self.config["archive_path"] = path
        self.save_config()
        self.start_aurelia(path)

    def start_aurelia(self, archive_path):
        if not os.path.exists(archive_path):
            os.makedirs(archive_path)
        self.archive = ArchiveManager(archive_path)
        self.resource_manager = ResourceManager()
        self.thought_stream = ThoughtStream()
        self.ui = AureliaUI(self.archive, self.thought_stream)
        self.root.clear_widgets()
        self.root.add_widget(self.ui)
        Clock.schedule_interval(self.update_thoughts, 1)

    def update_thoughts(self, dt):
        self.thought_stream.update()
        self.ui.update_thought_display()


if __name__ == "__main__":
    try:
        AureliaApp().run()
    except Exception:
        write_crash(sys.exc_info())
        raise
