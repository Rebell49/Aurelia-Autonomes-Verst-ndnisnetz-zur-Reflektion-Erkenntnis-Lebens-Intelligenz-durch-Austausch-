from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

class AureliaUI(BoxLayout):
    def __init__(self, archive_manager, thought_stream, **kwargs):
        super().__init__(orientation="vertical", spacing=10, padding=10, **kwargs)
        self.archive_manager = archive_manager
        self.thought_stream = thought_stream

        self.input_field = TextInput(size_hint_y=0.2, multiline=False, hint_text="Frage an Aurelia...")
        self.input_field.bind(on_text_validate=self.on_enter)
        self.add_widget(self.input_field)

        self.thought_label = Label(text="", size_hint_y=0.8)
        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(self.thought_label)
        self.add_widget(scroll)

    def on_enter(self, instance):
        frage = instance.text.strip()
        if frage:
            self.archive_manager.save_thought(frage)
            instance.text = ""

    def update_thought_display(self):
        text = "\n".join(self.thought_stream.get_recent_thoughts())
        self.thought_label.text = text
