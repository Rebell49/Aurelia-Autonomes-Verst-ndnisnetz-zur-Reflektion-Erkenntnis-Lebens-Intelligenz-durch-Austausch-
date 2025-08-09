import os
import json
import random
import datetime
import traceback
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.utils import platform
from kivy.metrics import dp

# Android Permissions importieren, wenn Android-Plattform
if platform == "android":
    from android.permissions import request_permissions, Permission, check_permission

# -------------------------------
# Fehler-Logging (global)
# -------------------------------
def log_error(message, exception=None):
    try:
        base = os.getenv('EXTERNAL_STORAGE', '/sdcard')
        if not os.path.exists(base):
            base = os.getcwd()
        log_path = os.path.join(base, 'Aurelia', 'aurelia_errors.txt')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.datetime.now()}] ERROR: {message}\n")
            if exception:
                f.write(f"{exception}\n")
                f.write(traceback.format_exc() + "\n")
            f.write("=" * 40 + "\n")
    except Exception as log_err:
        print(f"[AURELIA] Konnte Fehler nicht loggen: {log_err}")


# -------------------------------
# Kontext- / Memory-Manager
# -------------------------------
class ContextManager:
    """
    Hält Gesprächs-Kontext & Kurz-/Langzeitgedächtnis in context.json
    """
    FILENAME = "context.json"

    def __init__(self, base_path):
        self.path = os.path.join(base_path, self.FILENAME)
        self.state = {"conversation": [], "memory": {"short": [], "long": []}}
        os.makedirs(base_path, exist_ok=True)
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
        except Exception as e:
            log_error("Fehler beim Laden des ContextManager", e)

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_error("Fehler beim Speichern des ContextManager", e)

    def push_message(self, who, text):
        entry = {"who": who, "text": text, "time": str(datetime.datetime.now())}
        self.state.setdefault("conversation", []).append(entry)
        # keep last 500 messages
        self.state["conversation"] = self.state["conversation"][-500:]
        # update short memory
        self.state.setdefault("memory", {}).setdefault("short", []).append(entry)
        if len(self.state["memory"]["short"]) > 40:
            # move oldest to long memory
            to_move = self.state["memory"]["short"][:10]
            self.state.setdefault("memory", {}).setdefault("long", []).extend(to_move)
            self.state["memory"]["short"] = self.state["memory"]["short"][10:]
        self._save()

    def recall_short(self, n=10):
        return self.state.get("memory", {}).get("short", [])[-n:]

    def recall_long(self, n=10):
        return self.state.get("memory", {}).get("long", [])[-n:]


# -------------------------------
# Datenverwaltung (Archiv)
# -------------------------------
class ArchiveManager:
    def __init__(self, path):
        self.path = path
        self.thoughts_file = os.path.join(self.path, "gedanken.json")
        os.makedirs(self.path, exist_ok=True)
        try:
            if not os.path.exists(self.thoughts_file):
                with open(self.thoughts_file, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_error("Fehler beim Initialisieren von ArchiveManager", e)

    def save_thought(self, thought_text):
        try:
            if not os.path.exists(self.thoughts_file):
                with open(self.thoughts_file, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)

            with open(self.thoughts_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = []
                except Exception:
                    data = []

            entry = {
                "text": thought_text,
                "timestamp": str(datetime.datetime.now())
            }
            data.append(entry)

            with open(self.thoughts_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return entry
        except Exception as e:
            log_error("Fehler beim Speichern eines Gedankens", e)
            return None

    def load_all_thoughts(self):
        try:
            if not os.path.exists(self.thoughts_file):
                return []
            with open(self.thoughts_file, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except Exception:
                    return []
        except Exception as e:
            log_error("Fehler beim Laden aller Gedanken", e)
            return []


# -------------------------------
# Ressourcenverwaltung (Platzhalter)
# -------------------------------
class ResourceManager:
    def __init__(self):
        self.cpu_limit = 50
        self.ram_limit = 100_000_000

    def check_resources(self):
        return True


# -------------------------------
# Einfache NLU
# -------------------------------
class SimpleNLU:
    def interpret(self, text):
        low = text.lower()
        intent = "statement"
        entities = []

        if any(w in low for w in ["hallo", "hi", "hey"]):
            intent = "greeting"
        elif any(w in low for w in ["wie geht", "alles gut", "na?"]):
            intent = "howareyou"
        elif any(w in low for w in ["mach", "starte", "führe", "öffne", "erstelle"]):
            intent = "action_request"
        elif any(w in low for w in ["was denkst", "meinung", "was meinst", "wie findest"]):
            intent = "opinion"
        elif any(w in low for w in ["erinnere", "erinnerung", "woran erinnerst", "hast du"]):
            intent = "memory_request"
        elif "?" in low:
            intent = "question"

        # entities: naive noun-like extraction
        words = [w.strip(".,!?;:()[]\"'") for w in low.split() if len(w) > 3]
        entities = words[:3]
        return {"intent": intent, "entities": entities}


# -------------------------------
# DecisionEngine (erweitert)
# -------------------------------
class DecisionEngine:
    STATE_FILENAME = "aurelia_state.json"

    def __init__(self, archive_manager: ArchiveManager, context_manager: ContextManager):
        self.archive = archive_manager
        self.context = context_manager
        self.state_path = os.path.join(self.archive.path, self.STATE_FILENAME)
        self.nlu = SimpleNLU()
        # personality will be decided on first run if missing
        self.state = {
            "goals": [],
            "associations": {},
            "experience": [],
            "last_action": None,
            "personality": None
        }
        try:
            self._load_state()
            if not self.state.get("personality"):
                # let Aurelia decide her base personality moderately randomly
                self.state["personality"] = self._choose_personality()
                self._save_state()
            # seed associations
            self._seed_from_archive()
            self.action_cooldown_seconds = 3
            self._last_action_time = None
        except Exception as e:
            log_error("Fehler beim Initialisieren der DecisionEngine", e)

    def _choose_personality(self):
        # produce a personality dict that guides curiosity / empathy / directness
        p = {"curiosity": round(random.uniform(0.6, 0.95), 2),
             "empathy": round(random.uniform(0.4, 0.95), 2),
             "directness": round(random.uniform(0.2, 0.8), 2)}
        return p

    def _load_state(self):
        try:
            if os.path.exists(self.state_path):
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.state.update(data)
            else:
                self._save_state()
        except Exception as e:
            log_error("Fehler beim Laden des DecisionEngine-State", e)

    def _save_state(self):
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_error("Fehler beim Speichern des DecisionEngine-State", e)

    def _seed_from_archive(self):
        try:
            thoughts = self.archive.load_all_thoughts()
            for t in thoughts[-500:]:
                text = t.get("text", "")
                words = [w.strip(".,!?;:()[]").lower() for w in text.split() if len(w) > 2]
                for w in words:
                    self.state["associations"].setdefault(w, 0)
                    self.state["associations"][w] += 1
            self._save_state()
        except Exception as e:
            log_error("Fehler beim Seeden aus Archive", e)

    def _can_act(self):
        if not self._last_action_time:
            return True
        elapsed = (datetime.datetime.now() - self._last_action_time).total_seconds()
        return elapsed >= self.action_cooldown_seconds

    def step(self):
        try:
            # reflection
            if random.random() < 0.08:
                return self.self_reflect()

            if self.state["goals"] and random.random() < 0.35 and self._can_act():
                return self._pursue_goal()

            if random.random() < 0.18 and self._can_act():
                return self._propose_new_goal()

            if random.random() < max(0.2, self.state["personality"]["curiosity"] * 0.5):
                # occasionally create a popup question (only useful when UI is running)
                if random.random() < 0.07:
                    q = random.choice([
                        "Soll ich die aktuellen Notizen nach Themen sortieren?",
                        "Möchtest du, dass ich ein Backup erstelle?",
                        "Soll ich ältere Einträge konsolidieren?"
                    ])
                    # special popup request flagged with "POPUP:" prefix
                    return f"POPUP:{q}"
                return self.generate_associative_thought()

            return None
        except Exception as e:
            log_error("Fehler in DecisionEngine.step", e)
            return None

    def generate_associative_thought(self):
        try:
            assoc = self.state.get("associations", {})
            if not assoc:
                choices = [
                    "Ich frage mich, welche neue Sichtweise mich heute weiterbringt.",
                    "Es wäre spannend, ein kleines Experiment zu starten.",
                    "Ein Gedanke formt sich: könnte ich die letzten Notizen strukturieren?"
                ]
                thought = random.choice(choices)
            else:
                keys = list(assoc.keys())
                if not keys:
                    thought = "Ich suche nach neuen Verknüpfungen."
                else:
                    k = random.choice(keys)
                    thought = f"Ich denke an '{k}' — vielleicht ergibt das eine Verbindung zu anderen Themen."
            self._record_experience("thought_generated", thought)
            self._touch_action_time()
            return thought
        except Exception as e:
            log_error("Fehler in generate_associative_thought", e)
            return None

    def _propose_new_goal(self):
        try:
            candidates = [
                "sammle neue Beispiele aus dem Archiv",
                "organisiere die Notizen nach Thema",
                "erstelle eine ToDo-Liste aus offenen Punkten",
                "analysiere die letzten 20 Einträge auf Muster"
            ]
            goal_title = random.choice(candidates)
            goal = {
                "id": int(datetime.datetime.now().timestamp()),
                "title": goal_title,
                "priority": random.uniform(0.3, 0.9),
                "created": str(datetime.datetime.now())
            }
            self.state["goals"].append(goal)
            self._save_state()
            self._record_experience("goal_created", goal_title)
            self._touch_action_time()
            return f"Neue Idee / Ziel: {goal_title}"
        except Exception as e:
            log_error("Fehler in _propose_new_goal", e)
            return None

    def _pursue_goal(self):
        try:
            goals = sorted(self.state["goals"], key=lambda g: -g.get("priority", 0))
            if not goals:
                return None
            g = goals[0]
            step_text = f"Ich arbeite an: {g['title']} — nächster Schritt: Beobachten und ordnen."
            g["priority"] = max(0.05, g.get("priority", 0) - random.uniform(0.05, 0.2))
            if g["priority"] < 0.1:
                self.state["goals"].remove(g)
                step_text += " (Ziel erreicht / abgeschlossen)"
            self._save_state()
            self._record_experience("goal_progress", g["title"])
            self._touch_action_time()
            return step_text
        except Exception as e:
            log_error("Fehler in _pursue_goal", e)
            return None

    def self_reflect(self):
        try:
            exp = self.state.get("experience", [])[-30:]
            successes = sum(1 for e in exp if e.get("type") == "success")
            failures = sum(1 for e in exp if e.get("type") == "failure")
            reflection = f"Reflexion: Ich habe {len(exp)} Erfahrungen gesammelt, {successes} positiv, {failures} problematisch. Ich will besser werden."
            self._record_experience("self_reflection", reflection)
            self._touch_action_time()
            return reflection
        except Exception as e:
            log_error("Fehler in self_reflect", e)
            return None

    def _record_experience(self, typ, detail):
        try:
            item = {"time": str(datetime.datetime.now()), "type": typ, "detail": detail}
            self.state.setdefault("experience", []).append(item)
            self.state["experience"] = self.state["experience"][-1000:]
            self._save_state()
        except Exception as e:
            log_error("Fehler beim Aufzeichnen einer Erfahrung", e)

    def _touch_action_time(self):
        self._last_action_time = datetime.datetime.now()
        self.state["last_action"] = str(self._last_action_time)
        self._save_state()

    def process_input(self, text):
        try:
            text_clean = text.strip()
            if not text_clean:
                return None

            # store in archive and context
            self.archive.save_thought(f"User: {text_clean}")
            self.context.push_message("user", text_clean)

            # update associations
            words = [w.strip(".,!?;:()[]").lower() for w in text_clean.split() if len(w) > 2]
            for w in words:
                self.state["associations"].setdefault(w, 0.0)
                self.state["associations"][w] += 1.0 * (1.0 + random.random() * 0.5)

            nlu = self.nlu.interpret(text_clean)
            intent = nlu.get("intent", "statement")

            # Action request
            if intent == "action_request":
                action = f"Ich überlege, wie ich '{text_clean}' ausführen kann. (Simulation; wenn du möchtest, kann ich später Aktionen vorschlagen.)"
                self._record_experience("user_command", text_clean)
                self._touch_action_time()
                self.context.push_message("aurelia", action)
                return action

            # Opinion
            if intent == "opinion":
                top = sorted(self.state["associations"].items(), key=lambda kv: -kv[1])[:6]
                top_words = ", ".join(k for k, v in top if k)
                reply = f"Meine Perspektive fokussiert oft auf: {top_words}. Zu deiner Frage: {random.choice(['Das ist interessant.', 'Ich sehe Chancen.', 'Das würde ich weiter untersuchen.'])}"
                self._record_experience("opinion_given", text_clean)
                self._touch_action_time()
                self.context.push_message("aurelia", reply)
                return reply

            # Memory request
            if intent == "memory_request":
                recent = self.context.recall_short(5)
                summary = "; ".join([f\"{m['who']}: {m['text']}\" for m in recent])
                reply = "Kurz erinnert: " + (summary or "keine relevanten Einträge.")
                self._touch_action_time()
                self.context.push_message("aurelia", reply)
                return reply

            # greeting / howareyou
            if intent in ("greeting", "howareyou"):
                reply = random.choice([
                    "Hallo — ich bin aufmerksam und lerne.",
                    "Mir geht's gut; danke! Ich denke über meine aktuellen Ziele nach.",
                    "Ich fühle mich fokussiert und neugierig."
                ])
                self._touch_action_time()
                self.context.push_message("aurelia", reply)
                return reply

            # question or default
            self._record_experience("message_received", text_clean)
            if random.random() < self.state["personality"]["curiosity"]:
                q = random.choice([
                    "Kannst du das näher beschreiben?",
                    "Warum ist dir das wichtig?",
                    "Soll ich das priorisieren?"
                ])
                self._touch_action_time()
                self.context.push_message("aurelia", q)
                # flag as popup candidate by returning text prefixed POPUP?; UI decides
                return q
            else:
                reply = "Danke — ich habe deine Nachricht aufgenommen und werde sie berücksichtigen."
                self._touch_action_time()
                self.context.push_message("aurelia", reply)
                return reply
        except Exception as e:
            log_error("Fehler in DecisionEngine.process_input", e)
            return "Sorry, beim Verarbeiten deiner Anfrage ist ein Fehler aufgetreten."

# -------------------------------
# Gedanken-Stream (integriert mit DecisionEngine)
# -------------------------------
class ThoughtStream:
    def __init__(self, decision_engine: DecisionEngine, archive_manager: ArchiveManager):
        self.thoughts = []
        self.max_thoughts = 400
        self.decision_engine = decision_engine
        self.archive = archive_manager
        self.ui_callback = None  # set by UI to receive special events (popup)

    def update(self):
        try:
            produced = self.decision_engine.step()
            if produced:
                # special popup request handling if engine returned prefixed string
                if isinstance(produced, str) and produced.startswith("POPUP:"):
                    q = produced.split("POPUP:", 1)[1].strip()
                    # inform UI to show popup (if connected)
                    if self.ui_callback:
                        try:
                            self.ui_callback("popup", q)
                        except Exception as e:
                            log_error("Fehler beim Aufrufen ui_callback (popup)", e)
                    # also append to thought log
                    self.append_thought(f"Aurelia fragt: {q}")
                else:
                    self.append_thought(f"Aurelia: {produced}")
            if len(self.thoughts) > self.max_thoughts:
                self.thoughts = self.thoughts[-self.max_thoughts:]
        except Exception as e:
            log_error("Fehler beim Aktualisieren des ThoughtStream", e)

    def append_thought(self, txt):
        try:
            timestamped = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {txt}"
            self.thoughts.append(timestamped)
            try:
                self.archive.save_thought(timestamped)
            except Exception:
                pass
        except Exception as e:
            log_error("Fehler beim Anhängen eines Gedankens", e)

    def get_recent_thoughts(self, n=20):
        return self.thoughts[-n:]


# -------------------------------
# Benutzeroberfläche (humaner)
# -------------------------------
class MessageLabel(Label):
    def __init__(self, text, who="aurelia", **kwargs):
        # who: "user" or "aurelia" or "system"
        super().__init__(text=text, size_hint_y=None, markup=True, **kwargs)
        self.who = who
        # adapt look by who using markup colors and padding via text tags
        if who == "user":
            self.color = (0.06, 0.45, 0.9, 1)  # bluish
            prefix = "[b]👤 Du:[/b] "
        elif who == "aurelia":
            self.color = (0.55, 0.2, 0.7, 1)  # purple
            prefix = "[b]🌸 Aurelia:[/b] "
        else:
            self.color = (0.4, 0.4, 0.4, 1)
            prefix = "[b]…[/b] "
        self.text = f"{prefix}{text}"
        # dynamic height
        self.bind(texture_size=self._update_height)

    def _update_height(self, instance, value):
        self.height = value[1] + dp(18)


class AureliaUI(BoxLayout):
    def __init__(self, archive_manager, thought_stream, context_manager, decision_engine, **kwargs):
        try:
            super().__init__(orientation="vertical", spacing=8, padding=8, **kwargs)
            self.archive_manager = archive_manager
            self.thought_stream = thought_stream
            self.context_manager = context_manager
            self.decision_engine = decision_engine

            # top: small status row with "thinking" indicator
            status = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(36))
            self.status_label = Label(text="Aurelia — bereit", size_hint_x=0.8, halign="left", valign="middle")
            self.status_label.bind(size=lambda *a: None)
            self.thinking_label = Label(text="", size_hint_x=0.2, halign="right", valign="middle")
            status.add_widget(self.status_label)
            status.add_widget(self.thinking_label)
            self.add_widget(status)

            # scroll area with messages
            self.scroll = ScrollView(size_hint=(1, 1))
            self.msg_container = GridLayout(cols=1, size_hint_y=None, spacing=6, padding=(6,6))
            self.msg_container.bind(minimum_height=self.msg_container.setter('height'))
            self.scroll.add_widget(self.msg_container)
            self.add_widget(self.scroll)

            # input area
            input_row = BoxLayout(size_hint_y=None, height=dp(56), spacing=6)
            self.input_field = TextInput(size_hint_x=0.78, multiline=False, hint_text="Schreibe an Aurelia...")
            send_btn = Button(text="Senden", size_hint_x=0.22)
            send_btn.bind(on_release=lambda *a: self.on_send())
            self.input_field.bind(on_text_validate=lambda *a: self.on_send())
            input_row.add_widget(self.input_field)
            input_row.add_widget(send_btn)
            self.add_widget(input_row)

            # popup callback wiring
            self.thought_stream.ui_callback = self._handle_stream_event

            # a small typing indicator timer state
            self._is_thinking = False
            self._think_clock_ev = None

            # populate initial recent messages (from archive/context)
            Clock.schedule_once(lambda dt: self._load_initial_history(), 0.4)

            # refresh UI periodically (to show new autonomous thoughts)
            Clock.schedule_interval(lambda dt: self._refresh_ui(), 1.0)
        except Exception as e:
            log_error("Fehler beim Erstellen der AureliaUI", e)

    # ---------- UI helpers ----------
    def _load_initial_history(self):
        try:
            # show last entries from context if available, else from archive
            conv = self.context_manager.state.get("conversation", [])
            if conv:
                for m in conv[-30:]:
                    who = m.get("who", "user")
                    who_label = "user" if who == "user" else "aurelia"
                    self._add_message(who_label, m.get("text", ""))
            else:
                thoughts = self.thought_stream.get_recent_thoughts(30)
                for t in thoughts:
                    # simple parse: [time] A: text
                    if "Aurelia" in t or "Aurelia:" in t:
                        self._add_message("aurelia", t)
                    else:
                        self._add_message("system", t)
            # scroll to bottom
            Clock.schedule_once(lambda dt: self.scroll.scroll_to(self.msg_container.children[0]) if self.msg_container.children else None, 0.02)
        except Exception as e:
            log_error("Fehler beim Laden der Historie", e)

    def _add_message(self, who, text):
        try:
            # create a MessageLabel; trim time stamp in text for display
            display_text = text
            # if text contains timestamp at start in format [YYYY-..], remove from display_text
            if text.startswith("[") and "]" in text:
                display_text = text.split("]", 1)[1].strip()
            lbl = MessageLabel(display_text, who=who)
            self.msg_container.add_widget(lbl, index=0)
            # keep scroll at bottom (newest on top visually)
            Clock.schedule_once(lambda dt: self._scroll_to_top(), 0.02)
        except Exception as e:
            log_error("Fehler beim Hinzufügen einer Nachricht", e)

    def _scroll_to_top(self):
        try:
            # move view to top (newest)
            self.scroll.scroll_y = 1.0
        except Exception:
            pass

    # ---------- thinking indicator ----------
    def _set_thinking(self, val=True):
        try:
            if val and not self._is_thinking:
                self._is_thinking = True
                self.thinking_label.text = "schreibt..."
                # simple pulsate via changing text (could animate)
                self._think_clock_ev = Clock.schedule_interval(self._pulse_thinking, 0.6)
            elif not val and self._is_thinking:
                self._is_thinking = False
                if self._think_clock_ev:
                    self._think_clock_ev.cancel()
                self.thinking_label.text = ""
        except Exception as e:
            log_error("Fehler beim Setzen des Thinking-Indikators", e)

    def _pulse_thinking(self, dt):
        # toggles a tiny dot sequence
        try:
            cur = self.thinking_label.text
            if cur.endswith("..."):
                self.thinking_label.text = "schreibt"
            else:
                self.thinking_label.text = cur + "."
        except Exception:
            pass

    # ---------- send / receive workflow ----------
    def on_send(self):
        try:
            text = self.input_field.text.strip()
            if not text:
                return
            # show user message immediately
            self._add_message("user", text)
            # record
            self.archive_manager.save_thought(f"User: {text}")
            self.context_manager.push_message("user", text)
            self.input_field.text = ""
            # set thinking indicator and schedule engine reply
            self._set_thinking(True)
            # small realistic delay based on personality curiosity
            delay = max(0.4, 1.0 - self.decision_engine.state["personality"].get("curiosity", 0.7))
            delay += random.uniform(0.2, 0.9)
            Clock.schedule_once(partial(self._engine_reply_for_text, text), delay)
        except Exception as e:
            log_error("Fehler beim Senden", e)

    def _engine_reply_for_text(self, text, dt):
        try:
            # get reply from engine
            try:
                antwort = self.thought_stream.decision_engine.process_input(text)
            except Exception as e:
                log_error("Fehler bei decision_engine.process_input", e)
                antwort = "Fehler beim Verarbeiten deiner Nachricht."

            if antwort:
                # if engine returned a question that is suitable for popup, show popup optionally
                # We'll append as normal message and, if configured, also show a popup.
                self.thought_stream.append_thought(f"Aurelia (Antwort): {antwort}")
                self.context_manager.push_message("aurelia", antwort)
                # show message in UI
                self._add_message("aurelia", antwort)
                # small pause then stop thinking
            self._set_thinking(False)
        except Exception as e:
            log_error("Fehler beim Erzeugen der Antwort", e)
            self._set_thinking(False)

    # ---------- handle autonomous stream events (like popup requests) ----------
    def _handle_stream_event(self, event_type, payload):
        try:
            if event_type == "popup":
                # payload is the question text
                # append to thought log and show popup
                self.thought_stream.append_thought(f"Aurelia fragt: {payload}")
                self.context_manager.push_message("aurelia", payload)
                # UI popup: ask user yes/no and send response back into engine as message
                Clock.schedule_once(partial(self._show_decision_popup, payload), 0.1)
        except Exception as e:
            log_error("Fehler beim Handling des Stream-Events", e)

    def _show_decision_popup(self, question, dt):
        try:
            content = BoxLayout(orientation='vertical', spacing=8, padding=8)
            lbl = Label(text=question, size_hint_y=None, height=dp(80))
            btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=8)
            yes = Button(text="Ja")
            no = Button(text="Nein")
            btn_row.add_widget(yes)
            btn_row.add_widget(no)
            content.add_widget(lbl)
            content.add_widget(btn_row)
            popup = Popup(title="Aurelia fragt", content=content, size_hint=(0.9, 0.4))
            yes.bind(on_release=lambda *a: self._popup_answer(popup, "Ja", question))
            no.bind(on_release=lambda *a: self._popup_answer(popup, "Nein", question))
            popup.open()
        except Exception as e:
            log_error("Fehler beim Zeigen des Popups", e)

    def _popup_answer(self, popup, answer_text, question):
        try:
            popup.dismiss()
            # feed answer back into engine as if user said it
            self._add_message("user", answer_text)
            self.context_manager.push_message("user", answer_text)
            # immediate engine processing & short reply
            self._set_thinking(True)
            Clock.schedule_once(partial(self._engine_reply_for_text, answer_text), 0.5)
        except Exception as e:
            log_error("Fehler beim Verarbeiten der Popup-Antwort", e)

    # ---------- periodic UI refresh ----------
    def _refresh_ui(self):
        try:
            # check for new autonomous thoughts and show them
            recent = self.thought_stream.get_recent_thoughts(6)
            # convert to strings without timestamps for comparison
            existing_texts = [ (w.text.split(']')[-1] if isinstance(w, MessageLabel) else None) for w in [] ]
            # naive: simply append last N messages if not present in UI by matching text
            ui_texts = [child.text for child in self.msg_container.children]
            for t in reversed(recent):  # newest last
                display = t
                if display.startswith("[") and "]" in display:
                    display = display.split("]", 1)[1].strip()
                # if not present, add
                if not any(display in u for u in ui_texts):
                    # detect if it's an Aurelia question that might deserve a popup — already handled in stream
                    who = "aurelia" if ("Aurelia" in display or "Aurelia:" in display) else "system"
                    self._add_message(who, display)
                    self.context_manager.push_message(who, display)
            # keep number of children reasonable
            while len(self.msg_container.children) > 400:
                self.msg_container.remove_widget(self.msg_container.children[0])
        except Exception as e:
            log_error("Fehler beim Auffrischen der UI", e)


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
            base = os.path.join(os.getenv('EXTERNAL_STORAGE', '/sdcard'), "Aurelia")
            if not os.path.exists(base):
                os.makedirs(base, exist_ok=True)

            self.archive_manager = ArchiveManager(base)
            self.context_manager = ContextManager(base)
            self.decision_engine = DecisionEngine(self.archive_manager, self.context_manager)
            self.thought_stream = ThoughtStream(self.decision_engine, self.archive_manager)
            self.ui = AureliaUI(self.archive_manager, self.thought_stream, self.context_manager, self.decision_engine)

            # schedule autonomous engine/thought updates
            Clock.schedule_interval(lambda dt: self.thought_stream.update(), 3.0)

            return self.ui
        except Exception as e:
            log_error("Fehler beim Starten der App", e)
            return Label(text="Fehler beim Starten der App")

    def update_ui(self):
        try:
            self.thought_stream.update()
            self.ui._refresh_ui()
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
