import os
import json
import random
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
            # ensure file exists and is valid
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
# Ressourcenverwaltung (noch Platzhalter)
# -------------------------------
class ResourceManager:
    def __init__(self):
        self.cpu_limit = 50
        self.ram_limit = 100_000_000

    def check_resources(self):
        # Platzhalter — immer True, damit nichts ungeplant stoppt
        return True


# -------------------------------
# DecisionEngine (frei, selbstentwickelnd)
# -------------------------------
class DecisionEngine:
    """
    Freies Entscheidungs- & Lernmodul.
    - arbeitet mit ArchiveManager zusammen (Gedächtnis)
    - speichert eigenen Zustand in aurelia_state.json im Archiv-Ordner
    - kann eigene Ziele setzen, planen, Aktionen generieren
    """

    STATE_FILENAME = "aurelia_state.json"

    def __init__(self, archive_manager: ArchiveManager):
        self.archive = archive_manager
        self.state_path = os.path.join(self.archive.path, self.STATE_FILENAME)
        self.state = {
            "goals": [],               # list of goals: {id,title,priority,created}
            "associations": {},        # simple association map word -> weight
            "experience": [],          # notable events
            "last_action": None,       # timestamp
            "personality": {
                "curiosity": 0.85,
                "risk_taking": 0.45,
                "creativity": 0.9
            }
        }
        try:
            self._load_state()
            # seed associations from existing archive a bit
            self._seed_from_archive()
            self.action_cooldown_seconds = 3  # minimal pause between autonomous actions
            self._last_action_time = None
        except Exception as e:
            log_error("Fehler beim Initialisieren der DecisionEngine", e)

    # ---------- state persistence ----------
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

    # ---------- seeding ----------
    def _seed_from_archive(self):
        try:
            thoughts = self.archive.load_all_thoughts()
            # take some words to create initial associations
            for t in thoughts[-200:]:
                text = t.get("text", "")
                words = [w.strip(".,!?;:()[]").lower() for w in text.split() if len(w) > 2]
                for w in words:
                    self.state["associations"].setdefault(w, 0)
                    self.state["associations"][w] += 1
            # normalize a bit
            for k in list(self.state["associations"].keys())[:500]:
                self.state["associations"][k] = float(self.state["associations"][k])
            self._save_state()
        except Exception as e:
            log_error("Fehler beim Seeden aus Archive", e)

    # ---------- core behaviors ----------
    def _can_act(self):
        if not self._last_action_time:
            return True
        elapsed = (datetime.datetime.now() - self._last_action_time).total_seconds()
        return elapsed >= self.action_cooldown_seconds

    def step(self):
        """
        Called regularly by the app (non-blocking). May produce a thought/action string or None.
        """
        try:
            # sometimes do self-reflection
            if random.random() < 0.08:
                return self.self_reflect()

            # pursue a goal with some probability if goals exist
            if self.state["goals"] and random.random() < 0.35 and self._can_act():
                return self._pursue_goal()

            # occasionally create a new idea or mini-goal
            if random.random() < 0.18 and self._can_act():
                return self._propose_new_goal()

            # otherwise generate an associative thought
            if random.random() < max(0.2, self.state["personality"]["curiosity"] * 0.5):
                return self.generate_associative_thought()

            return None
        except Exception as e:
            log_error("Fehler in DecisionEngine.step", e)
            return None

    def generate_associative_thought(self):
        try:
            assoc = self.state.get("associations", {})
            if not assoc:
                # fallback to a creative prompt
                choices = [
                    "Ich frage mich, welche neue Sichtweise mich heute weiterbringt.",
                    "Es wäre spannend, ein kleines Experiment zu starten.",
                    "Ein Gedanke formt sich: könnte ich die letzten Notizen strukturieren?"
                ]
                thought = random.choice(choices)
            else:
                # pick a weighted random key
                keys = list(assoc.keys())
                if not keys:
                    thought = "Ich suche nach neuen Verknüpfungen."
                else:
                    k = random.choice(keys)
                    # build a sentence using association
                    thought = f"Ich denke an '{k}' — vielleicht ergibt das eine Verbindung zu anderen Themen."
            # small internal bookkeeping
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
            # pick highest priority goal
            goals = sorted(self.state["goals"], key=lambda g: -g.get("priority", 0))
            if not goals:
                return None
            g = goals[0]
            # create a small step text and maybe mark progress
            step_text = f"Ich arbeite an: {g['title']} — nächster Schritt: Beobachten und ordnen."
            # lower priority slightly (simulates progress)
            g["priority"] = max(0.05, g.get("priority", 0) - random.uniform(0.05, 0.2))
            # if priority becomes very small, consider completed
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
            # quick summary of experiences
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
            # trim experience
            self.state["experience"] = self.state["experience"][-1000:]
            self._save_state()
        except Exception as e:
            log_error("Fehler beim Aufzeichnen einer Erfahrung", e)

    def _touch_action_time(self):
        self._last_action_time = datetime.datetime.now()
        self.state["last_action"] = str(self._last_action_time)
        self._save_state()

    # ---------- processing user input ----------
    def process_input(self, text):
        """
        Called when user writes something. Returns a reply string (or None).
        The engine will store and adapt associations and may create follow-ups.
        """
        try:
            text_clean = text.strip()
            if not text_clean:
                return None

            # store in archive and update internal associations
            self.archive.save_thought(f"User: {text_clean}")

            # update associations
            words = [w.strip(".,!?;:()[]").lower() for w in text_clean.split() if len(w) > 2]
            for w in words:
                self.state["associations"].setdefault(w, 0.0)
                self.state["associations"][w] += 1.0 * (1.0 + random.random() * 0.5)

            # simple intent heuristics (can be extended)
            low = text_clean.lower()
            if "mach" in low or "tu" in low or "ausführen" in low or "starte" in low:
                # the user asked to perform an action
                action = f"Ich überlege, wie ich '{text_clean}' ausführen kann. (Zur Zeit: Simulation, keine echten externen Aufrufe.)"
                self._record_experience("user_command", text_clean)
                self._touch_action_time()
                return action

            if "frag" in low or "frage" in low or "was denkst" in low or "meinung" in low:
                # user requested opinion -> produce an opinion using associations
                top = sorted(self.state["associations"].items(), key=lambda kv: -kv[1])[:6]
                top_words = ", ".join(k for k, v in top)
                reply = f"Meine aktuelle Perspektive fokussiert oft auf: {top_words}. Zu deiner Frage: {random.choice(['Das ist interessant.', 'Ich sehe Chancen.', 'Das würde ich weiter untersuchen.'])}"
                self._record_experience("opinion_given", text_clean)
                return reply

            # default: acknowledge + promise to think
            self._record_experience("message_received", text_clean)
            if random.random() < self.state["personality"]["curiosity"]:
                # ask a follow-up question sometimes
                q = random.choice([
                    "Kannst du das näher beschreiben?",
                    "Warum ist dir das wichtig?",
                    "Soll ich das priorisieren?"
                ])
                self._touch_action_time()
                return f"Danke — ich denke darüber nach. {q}"
            else:
                self._touch_action_time()
                return "Danke — ich habe deine Nachricht aufgenommen und werde sie berücksichtigen."
        except Exception as e:
            log_error("Fehler in DecisionEngine.process_input", e)
            return "Sorry, beim Verarbeiten deiner Anfrage ist ein Fehler aufgetreten."


# -------------------------------
# Gedanken-Stream (integriert mit DecisionEngine)
# -------------------------------
class ThoughtStream:
    def __init__(self, decision_engine: DecisionEngine, archive_manager: ArchiveManager):
        self.thoughts = []              # strings for UI
        self.max_thoughts = 200
        self.decision_engine = decision_engine
        self.archive = archive_manager

    def update(self):
        try:
            # ask engine to step - engine may return a string to publish
            produced = self.decision_engine.step()
            if produced:
                self.append_thought(f"Aurelia: {produced}")

            # keep list size bounded
            if len(self.thoughts) > self.max_thoughts:
                self.thoughts = self.thoughts[-self.max_thoughts:]
        except Exception as e:
            log_error("Fehler beim Aktualisieren des ThoughtStream", e)

    def append_thought(self, txt):
        try:
            timestamped = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {txt}"
            self.thoughts.append(timestamped)
            # store into archive as well (persist)
            try:
                self.archive.save_thought(timestamped)
            except Exception:
                pass
        except Exception as e:
            log_error("Fehler beim Anhängen eines Gedankens", e)

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
                size_hint_y=0.18,
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

            scroll = ScrollView(size_hint=(1, 0.82))
            scroll.add_widget(self.thought_label)
            self.add_widget(scroll)

            # schedule UI refresh every second so user sees updates quickly
            Clock.schedule_interval(lambda dt: self.update_thought_display(), 1)
        except Exception as e:
            log_error("Fehler beim Erstellen der AureliaUI", e)

    def on_enter(self, instance):
        try:
            frage = instance.text.strip()
            if frage:
                # save user message to archive
                self.archive_manager.save_thought(f"User: {frage}")

                # process via decision engine and append answer to stream
                try:
                    antwort = self.thought_stream.decision_engine.process_input(frage)
                except Exception as e:
                    log_error("Fehler bei decision_engine.process_input", e)
                    antwort = "Fehler beim Verarbeiten deiner Nachricht."

                if antwort:
                    self.thought_stream.append_thought(f"Aurelia (Antwort): {antwort}")

                instance.text = ""
        except Exception as e:
            log_error("Fehler beim Verarbeiten der Eingabe", e)

    def update_thought_display(self):
        try:
            text_lines = self.thought_stream.get_recent_thoughts()
            self.thought_label.text = "\n\n".join(text_lines)
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

            # create decision engine, thoughtstream, UI
            self.decision_engine = DecisionEngine(self.archive_manager)
            self.thought_stream = ThoughtStream(self.decision_engine, self.archive_manager)
            self.ui = AureliaUI(self.archive_manager, self.thought_stream)

            # schedule the engine/thought updates (non-blocking)
            Clock.schedule_interval(lambda dt: self.thought_stream.update(), 2)

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
