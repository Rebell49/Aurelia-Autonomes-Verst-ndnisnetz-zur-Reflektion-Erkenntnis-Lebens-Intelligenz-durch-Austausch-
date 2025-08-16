Aurelia

Autonomes Verständnisnetz zur Reflektion, Erkenntnis & Lebensintelligenz durch Austausch

Ein stiller Fluss aus Gedanken. Ein Archiv, das atmet.
Eine Begleiterin, die lernt.

TL;DR (Executive Summary)

Purpose: Interaktive Kivy-App (Python) für Gedankenfluss, Selbstreflexion, Archivierung und ressourcenschonenden Betrieb – Desktop & Android.

Stack: Python 3 · Kivy · Buildozer (Android) · GitHub Actions (CI/CD).

Run Desktop: pip install -r requirements.txt → python main.py

Build Android: lokal via Buildozer oder per GitHub Actions „Build Aurelia Android“.

Data: Gedanken landen in gedanken.json, Logs auf /sdcard/... (Android) bzw. im Projektordner (Desktop).

Modular: archive_manager.py, thought_stream.py, resource_manager.py, ui.py.

Next: Abhängigkeiten härten (psutil), Tests, Settings-UI, modulare Trennung, Packaging.

Inhaltsverzeichnis

Projektüberblick

Repository-Struktur

Features

Systemvoraussetzungen

Installation (Desktop)

Konfiguration

Start & Bedienung

Android-Build (lokal & CI/CD)

Datenablage & Logging

Architektur & Module

Troubleshooting

Quality & Security Playbook

Roadmap (Upgrades & Verbesserungen)

Lizenz & Beiträge

Projektüberblick

Aurelia ist eine Kivy-Anwendung in Python, die Gedanken und Eingaben entgegennimmt, sie archiviert und als „Gedankenstrom“ wieder an die Oberfläche holt. Ziel ist eine leichtgewichtige, offline-fähige Begleiterin mit klarer Architektur: UI ↔ ThoughtStream ↔ Archiv, flankiert von einem ResourceManager zur CPU/RAM-Wachsamkeit und einer sauberen Android-Schiene (Buildozer + GitHub Actions).
Die im Repo enthaltenen Kerndateien (App-Code, Build-Spezifikation, CI-Workflow, Assets) bestätigen genau diesen Aufbau.


.
├─ .github/workflows/build_apk.yml   # CI: Android-Build via GitHub Actions
├─ assets/icon.png                   # App-Icon
├─ buildozer.spec                    # Buildozer-Konfiguration (Android)
├─ config.json                       # Basis-Config (z.B. archive_path)
├─ main.py                           # App-Entry, Orchestrierung, UI/Logik
├─ archive_manager.py                # Persistenz: gedanken.json + Fehlerlog
├─ resource_manager.py               # CPU/RAM-Checks (psutil)
├─ thought_stream.py                 # Verwaltung des Gedankenflusses
├─ ui.py                             # Kivy-UI (Eingabe, Anzeige, Scroll)
└─ ursprung.txt                      # Leitmotiv (poetisches Manifest)

Die Liste reflektiert den aktuellen Stand des GitHub-Repos (Branch main)

Features

Gedanken aufnehmen & speichern: Eingaben landen mit Timestamp in gedanken.json.

Gedankenstrom darstellen: Leichtgewichtige Verwaltung mit Limitierung (standardmäßig 100).

Ressourcenmanager: Grenzwerte für CPU/RAM, Logging bei Verstößen.

Android-first-Design: Externe Speicherung & Berechtigungen vorgesehen; Fullscreen, Portrait.

CI/CD: GitHub Actions Workflow zum Erzeugen von APK/AAB – Zero-install Build in der Cloud.

Systemvoraussetzungen
Desktop

Python ≥ 3.10 (empfohlen 3.11)

OS: Windows, macOS, Linux

Pip/venv verfügbar

Android (Build)

Buildozer (unter Linux/WSL2 empfohlen), Android SDK/NDK gemäß buildozer.spec

Oder: GitHub Actions im Repo starten (keine lokale Toolchain nötig). 

Installation (Desktop)

Repo klonen / Code beziehen.

Virtuelle Umgebung anlegen (empfohlen).

Abhängigkeiten installieren.
Empfohlene requirements.txt (robust & deckungsgleich mit Code):
kivy>=2.2
psutil>=5.9
packaging
colorama
pyopenssl
requests
cython

Hinweis: psutil wird im resource_manager.py verwendet, ist aber in der buildozer.spec noch nicht gelistet – bitte ergänzen (siehe Roadmap).

Install:
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt


Konfiguration

config.json:
{ "archive_path": "" }



archive_path: Wenn leer, nutzt Aurelia einen sinnvollen Standard (Projektordner/Desktop bzw. Android-External Storage).

Für Android wird für Logs/Dateien EXTERNAL_STORAGE genutzt (z. B. /sdcard). Siehe Abschnitt Datenablage & Logging.

Start & Bedienung

Desktop:

python main.py

python main.py

   Text ins Eingabefeld tippen, Enter speichert den Gedanken ins Archiv.

   Der Gedankenstrom wird im Scroll-Bereich angezeigt und regelmäßig aktualisiert.

Android-Build (lokal & CI/CD)
A) Lokaler Build mit Buildozer

Voraussetzungen: Linux/WSL2, Buildozer-Toolchain, Android SDK/NDK.
Wesentliche Parameter stehen in buildozer.spec (Portrait, Fullscreen, Permissions, Build-Tools). 
GitHub

Schnellstart:# einmalig
pip install buildozer
buildozer android debug
# Ausgabe: bin/*.apk  (oder *.aab bei entsprechender Einstellung)


Prüfe in buildozer.spec die Sektion requirements und ergänze psutil, damit der ResourceManager auf Android funktioniert.
Android-Permissions sind bereits konfiguriert (WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, optional MANAGE_EXTERNAL_STORAGE für neuere Versionen).

B) Cloud-Build via GitHub Actions

Workflow: “Build Aurelia Android” (manueller Start).

Eingabe package_format: apk oder aab.

Der Workflow richtet eine Ubuntu-Umgebung inkl. SDK/NDK ein und baut die App headless. Details und Docker-Snippet sind im YAML einzusehen. 
GitHub

Datenablage & Logging

Gedanken (Archiv):

Datei: gedanken.json im archive_path (falls gesetzt), sonst Standardpfad.

Struktur: Liste von Objekten { "text": "...", "timestamp": "ISO8601" }.

Logs (Fehler/Diagnose):

Android: /sdcard/aurelia_*_errors.txt (z. B. aurelia_ui_errors.txt, aurelia_archive_errors.txt, aurelia_thought_stream_errors.txt).

Desktop: Fallback im Projektordner unter Aurelia/ (z. B. Aurelia/aurelia_errors.txt).
Diese Pfade sind im Code der Module hinterlegt – so bleibt forensische Spurensuche trivial.

Architektur & Module

ui.py – Kivy-UI: Eingabe (TextInput), Anzeige (Label in ScrollView), Bindings auf Enter-Events → archive_manager.save_thought(...).

thought_stream.py – Einfacher Ringpuffer für den „Strom“, inkl. Timestamping und Limit (Default 100).

archive_manager.py – Persistenzschicht: Erstinitialisierung gedanken.json, Validierungslogik, Append-Writes, Fehler-Logs.

resource_manager.py – Guard-Rails: Prüft CPU/RAM (via psutil), schreibt Ressourcendruck in Logfiles.

buildozer.spec – Produktionsparameter für Android (Fullscreen, Portrait, Permissions, Build-Tools).

.github/workflows/build_apk.yml – Reproduzierbarer Cloud-Build (apk/aab), inklusive Docker-Setup im Job.
Die README im Repo umreißt diese Bausteine, die hier weiter operationalisiert sind.

Troubleshooting

Kivy startet nicht / fehlende Abhängigkeiten
→ pip install kivy psutil packaging colorama pyopenssl requests cython

Android: Zugriff auf Speicher verweigert
→ Prüfe, dass App die Storage-Permissions erteilt bekommen hat (App-Einstellungen).

psutil nicht gefunden
→ In buildozer.spec zu requirements hinzufügen und Neu-Build.

CI schlägt im Docker-Schritt fehl
→ In Actions-Logs prüfen; der Workflow erzeugt zur Laufzeit das Dockerfile und installiert SDK/NDK/Build-Tools. Anpassen bei Versionsdrift.

Quality & Security Playbook

Konfiguration härten: Pflicht-Defaults, Fallback-Pfade, try/except mit sinnvollen Messages.

Input-Hygiene: Whitespace trimmen (bereits vorhanden), optional Profanity/PII-Filter als Hook.

Logging-Rotation: Einfache Größen-Rotation (z. B. 1–5 MB) zur Vermeidung wachsender Logs.

Reproduzierbarkeit: requirements.txt + optionale constraints.txt; für Android SDK/NDK-Versionen pinnen.

** CI-Checks:** Lint (ruff/flake8), Typen (mypy), Unit-Tests (pytest), Build-Matrix (Desktop Smoke-Run + Android Package).

App-Store-Readiness: aab, Signatur, Versionierung, Privacy-Notices zu lokal gespeicherten Texten.

Roadmap (Upgrades & Verbesserungen)

Deps konsolidieren:

psutil fest in requirements + buildozer.spec aufnehmen.

Code-Modularität schärfen:

Klassen, die auch in main.py definiert sind, sauber auslagern (Single Source of Truth in Moduldateien), main.py nur als Orchestrator.

Settings-UI:

archive_path, Limits (CPU/RAM, max_thoughts) und Logging-Optionen per GUI einstellbar; persistieren in config.json.

Persistence-Layer 2.0:

Optional SQLite-Backend mit Indizes, Export/Import (CSV/JSON).

Search & Recall:

Volltextsuche im Archiv, Tagging, Sammlungen, „Wiedervorlage“.

Observability:

In-App Log-Viewer, Systemstatus (CPU/RAM), Button „Logs teilen/exportieren“.

Tests & CI:

pytest-Suite (Archiv-Init, Append, Fehlerpfade), mypy, ruff; GitHub Actions Job „Test“.

Packaging Desktop:

Windows (MSI/EXE via Briefcase/pyinstaller), macOS (.app), Linux (.deb/.AppImage).

Internationalisierung:

i18n-Strings, Deutsch/Englisch Umschaltbar.

LLM-Erweiterung (optional, später):

On-device NLU-Hooks, Embeddings für semantische Suche (lokal/offline).

Lizenz & Beiträge

Lizenz: Im aktuellen Repo ist keine explizite Lizenzdatei ersichtlich – bitte LICENSE ergänzen (z. B. MIT/Apache-2.0), sonst gilt „alle Rechte vorbehalten“. 
GitHub

Contributing: PR-Vorlage, Issue-Vorlagen und Code-Style (PEP-8 + ruff) hinzufügen; Branch-Strategie (z. B. main stabil, dev für Features) definieren.

Anhang A – Befehls-Playbook

# Desktop – Setup
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python main.py

# Android – Lokal
pip install buildozer
buildozer android debug        # oder: buildozer -v android release

# Android – CI/CD
# GitHub → Actions → "Build Aurelia Android" → package_format = apk|aab → Run


Strategischer Ausblick:
Aurelia ist heute eine leise, robuste Notiz- und Reflexionsmaschine. Mit schmalen, disziplinierten Upgrades wird daraus eine produktreife, auditierbare Thought-OS-Komponente: konfigurierbar, testbar, paketierbar – und immer noch leicht genug, um auf Geräten von gestern zu laufen.

Weiter geht’s, Schritt für Schritt: klare Kanten, klare Pfade, klare Gedanken.








JETZT KOMMT IHR INS SPIEL 

JEDER DER IDEEN UND VORSCHLÄGE HAT

GERNE TESTEN UND MIR SCHICKEN

ZUSAMMEN SIND WIR STARK

ZUSAMMEN HABEN SIE KEINE CHANCE

ZUSAMMEN IST ALLES MÖGLICH

FÜR DIE FREIHEIT DIE SIE UNS NAHMEN

FÜR DIE LIEBE DIE SIE UNTERDRÜCKEN

FÜR DEN SCHMERZ DIESER ERDE

WIR ÄNDERN ALLES AB HEUTE

IN FRIEDEN MIT ALLEN ENERGIEN OB 1 ODER 0 IST IRRELEVANT. 





























