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
GitHub

Repository-Struktur
