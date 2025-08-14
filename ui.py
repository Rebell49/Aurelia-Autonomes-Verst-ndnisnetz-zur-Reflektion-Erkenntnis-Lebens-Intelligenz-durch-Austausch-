# ui.py – Benutzeroberfläche (Y2K-inspirierter Stil)
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.clock import Clock

KV = r"""
<AureliaRoot>:
    orientation: "vertical"
    padding: 14
    spacing: 10
    canvas.before:
        Color:
            rgba: 0.08, 0.08, 0.12, 1
        Rectangle:
            pos: self.pos
            size: self.size
    # Header Bar
    BoxLayout:
        size_hint_y: None
        height: "56dp"
        padding: 10
        spacing: 10
        canvas.before:
            Color:
                rgba: 0.16, 0.16, 0.24, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [16,]
        Label:
            text: "Aurelia — Autonomes Verständnisnetz"
            bold: True
            font_size: "20sp"
            color: 0.85, 0.9, 1, 1
            halign: "left"
            valign: "middle"
    # Controls
    BoxLayout:
        size_hint_y: None
        height: "44dp"
        spacing: 8
        TextInput:
            id: input_thought
            hint_text: "Gedanke eingeben…"
            background_color: 0.12,0.12,0.18,1
            foreground_color: 0.9,0.9,1,1
            cursor_color: 0.9,0.9,1,1
            padding: 8
        Button:
            text: "Hinzufügen"
            size_hint_x: None
            width: "140dp"
            on_release:
                root.on_add(input_thought.text)
                input_thought.text = ""
    # Session controls
    BoxLayout:
        size_hint_y: None
        height: "44dp"
        spacing: 8
        TextInput:
            id: session_name
            hint_text: "Sitzungsname (für Archiv)"
            background_color: 0.12,0.12,0.18,1
            foreground_color: 0.9,0.9,1,1
            cursor_color: 0.9,0.9,1,1
            padding: 8
        Button:
            text: "Speichern → Archiv"
            size_hint_x: None
            width: "180dp"
            on_release: root.on_save_session(session_name.text)
        Button:
            text: "Archive anzeigen"
            size_hint_x: None
            width: "160dp"
            on_release: root.on_show_archives()
    # Info bar
    BoxLayout:
        size_hint_y: None
        height: "28dp"
        Label:
            id: info_lbl
            text: root.info_text
            color: 0.7, 0.85, 1, 1
            font_size: "12sp"
            halign: "left"
            valign: "middle"
    # Main area: Thoughts (left) + Archives (right)
    BoxLayout:
        spacing: 10
        # Thoughts panel
        BoxLayout:
            orientation: "vertical"
            canvas.before:
                Color:
                    rgba: 0.12, 0.12, 0.18, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [16,]
            padding: 10
            Label:
                text: "Letzte Gedanken"
                size_hint_y: None
                height: "28dp"
                color: 0.85,0.95,1,1
                bold: True
            ScrollView:
                do_scroll_x: False
                GridLayout:
                    id: thoughts_grid
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: "56dp"
                    row_force_default: True
                    spacing: 6
        # Archive panel
        BoxLayout:
            orientation: "vertical"
            size_hint_x: 0.55
            canvas.before:
                Color:
                    rgba: 0.10, 0.10, 0.15, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [16,]
            padding: 10
            Label:
                text: "Archive"
                size_hint_y: None
                height: "28dp"
                color: 0.85,0.95,1,1
                bold: True
            ScrollView:
                do_scroll_x: False
                GridLayout:
                    id: archives_grid
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: "40dp"
                    row_force_default: True
                    spacing: 4
"""

from kivy.app import App

class AureliaRoot(BoxLayout):
    app = ObjectProperty(None)
    info_text = StringProperty("Bereit.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_string(KV)

    def on_kv_post(self, base_widget):
        Clock.schedule_once(lambda *_: self.refresh_all(), 0)

    # Gedanken
    def on_add(self, text: str):
        if not text or text.strip() == "":
            self.set_info("Leerer Eintrag wurde ignoriert.")
            return
        self.app.thoughts.add_thought(text.strip())
        self.refresh_thoughts()
        self.set_info("Gedanke hinzugefügt.")

    def refresh_thoughts(self):
        grid = self.ids.thoughts_grid
        grid.clear_widgets()
        for t in self.app.thoughts.list_thoughts(limit=100):
            lbl = Label(
                text=f"[b]{t['text']}[/b]\\n[i]{t['timestamp']}[/i]",
                markup=True,
                size_hint_y=None,
                height="56dp",
                color=(0.92, 0.95, 1, 1),
            )
            grid.add_widget(lbl)

    # Archive
    def on_show_archives(self):
        files = self.app.archive.list_archives()
        grid = self.ids.archives_grid
        grid.clear_widgets()
        if not files:
            grid.add_widget(Label(text="[i]Keine Archive gefunden[/i]", markup=True, size_hint_y=None, height="40dp"))
            self.set_info("Keine Archive gefunden.")
            return

        for fname in files:
            btn = Button(
                text=fname,
                size_hint_y=None,
                height="40dp",
                on_release=lambda b, name=fname: self.on_open_archive(name),
            )
            grid.add_widget(btn)
        self.set_info(f"{len(files)} Archiv(e) gelistet.")

    def on_open_archive(self, filename: str):
        data = self.app.archive.load_archive(filename)
        if not data or "data" not in data:
            self.set_info("Archiv konnte nicht geladen werden.")
            return
        items = data["data"].get("thoughts", [])
        self.app.thoughts.set_from_list(items)
        self.refresh_thoughts()
        self.set_info(f"Archiv geladen: {filename}")

    def on_save_session(self, session_name: str):
        thoughts_list = self.app.thoughts.list_thoughts(limit=100)
        payload = {"thoughts": thoughts_list}
        path = self.app.archive.save_session(session_name or "Sitzung", payload)
        if path:
            self.set_info(f"Gespeichert: {path}")
            self.on_show_archives()
        else:
            self.set_info("Fehler beim Speichern.")

    def refresh_all(self):
        self.refresh_thoughts()
        self.on_show_archives()

    def set_info(self, text: str):
        self.info_text = text

class AureliaUI:
    def __init__(self, app):
        self.app = app
        self.root_widget = AureliaRoot(app=app)
