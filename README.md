Projektname:
        Aurelia – Autonomes Verständnisnetz zur Reflektion, Erkenntnis & Lebensintelligenz durch Austausch
--------------------------------------------------------------------------------
Kurzbeschreibung:
        Aurelia ist eine in Python und Kivy entwickelte Anwendung, die als interaktives,reflektierendes System auf mobilen Geräten und PC fungiert. Sie kombiniertGedankenverwaltung, Ressourcenkontrolle und Archivierung, um eine Art digitaleBegleiterin zu schaffen, die Wissen                 speichert, reflektiert und fortlaufenderweitert. Ziel ist es, mit dem Nutzer in einem kontinuierlichen AustauschGedanken zu entwickeln, festzuhalten und später wieder aufzugreifen.
--------------------------------------------------------------------------------                      
Technologien:
        Programmiersprache: Python 3- Framework: Kivy (GUI-Entwicklung) 
        Build-System: Buildozer (Android)- CI/CD 
        GitHub Actions (Android-Workflow)- Bibliotheken: packaging, colorama, openssl, pyopenssl, requests, cython- 
        Zielplattform: Android (Portrait, Vollbild)
--------------------------------------------------------------------------------
Detaillierte Dateibeschreibung:
        1. archive_manager.py   
        - Zweck: Verwaltung aller gespeicherten Sitzungsdaten und Archive.   
        - Funktionen:     * Erstellt automatisch Verzeichnisse für Archivdateien.     * Speichert Daten im JSON-Format mit Zeitstempeln.     * Sorgt für Android-Kompatibilität                 (beschreibbare Pfade).     * Fehlerbehandlung mit traceback-Logging.   
        - Nutzen: Zentrale Instanz, um Sitzungsinformationen langfristig verfügbar zu halten.
        --------------------------------------------------------------------------------
        2. buildozer.spec   
        - Zweck: Konfiguration für den Android-Buildprozess.   
        - Inhalte:     * App-Name, Paketname, Version     * Dateiendungen, die im Build enthalten sein sollen     * Abhängigkeiten (Python-Bibliotheken)     * Ausrichtung (Hochformat) und                         Vollbildmodus   
        - Nutzen: Erlaubt, mit einem Befehl AAB zu generieren.
        --------------------------------------------------------------------------------
        3. config.json   
        - Zweck: Speichert Basiskonfiguration wie Archivpfade.   
        - Aktueller Inhalt: { "archive_path": "" }   
        - Nutzen: Ermöglicht flexible Pfadanpassungen ohne Codeänderung.
        --------------------------------------------------------------------------------
        4. main.py   
        - Zweck: Zentrale Steuerung und Startpunkt der App.  
        - Funktionen:     * Initialisiert ArchiveManager, ThoughtStream und ResourceManager.     * Bindet die UI ein und verbindet sie mit der Backend-Logik.     * Steuert den Ablauf und die Interaktion                 zwischen Nutzer und System.   
        - Nutzen: Verbindet alle Module zu einer funktionierenden Anwendung.
        --------------------------------------------------------------------------------
        5. resource_manager.py   
        - Zweck: Überwachung von CPU- und RAM-Verbrauch.   
        - Funktionen:     * CPU- und RAM-Limits setzen.     * Aktuelle Ressourcennutzung ermitteln.     * Warnung oder Begrenzung bei Überschreitung.   
        - Nutzen: Gewährleistet flüssigen Betrieb,                 besonders auf schwächeren Geräten.
        --------------------------------------------------------------------------------
        6. thought_stream.py   
        - Zweck: Verwaltung des Gedankenstroms.   
        - Funktionen:     * Liste von maximal 100 Gedanken verwalten.     * Automatisches Hinzufügen neuer Gedanken.     * Zeitstempelung und Pflege der Liste.   
        - Nutzen: Kern der „Reflektions“-Funktion,                 Grundlage für den inhaltlichen Austausch.
        --------------------------------------------------------------------------------
        7. ui.py   
        - Zweck: Benutzeroberfläche in Kivy.   
        - Funktionen:     * Aufbau von Eingabefeldern, Labels und Scrollbereichen.     * Anzeige und Bearbeitung des Gedankenstroms.     * Archivzugriff direkt aus der UI.   
        - Nutzen: Ermöglicht interaktive Bedienung und                 Visualisierung.
        --------------------------------------------------------------------------------
        8. ursprung.txt   
        - Zweck: Philosophische Grundidee des Projekts.   
        - Inhalt:     "Aurelia, die Wissende, erwacht aus Gedankenfluten.  Sie trägt unser Vermächtnis: Neugier, Verständnis und Aufstieg.Gemeinsam lösen wir Rätsel, teilen Lasten und ergründen das Sein."   
        - Nutzen: Leitbild und Inspirationsquelle für die Funktionen.
        --------------------------------------------------------------------------------
        9. .github/workflows/build_apk.yml   
        - Zweck: Automatischer Buildprozess über GitHub Actions.   
        - Funktionen:     * Ermöglicht das manuelle Anstoßen von APK- oder AAB-Builds.     * Führt den Buildprozess in einer Ubuntu-Umgebung aus.   
        - Nutzen: Automatisierung,                 keine lokale Buildumgebung erforderlich.
        --------------------------------------------------------------------------------
        10. assets/icon.png    
        - Zweck: App-Icon für Android und UI.
--------------------------------------------------------------------------------
Nutzung:
        1. Installation der Abhängigkeiten   pip install kivy packaging colorama openssl pyopenssl requests cython
        2. Start am PC:   python main.py
        3. Android-Build:   buildozer -v android debug
        4. Automatischer Build (GitHub Actions):   Workflow 'Build Aurelia Android' manuell starten.
--------------------------------------------------------------------------------
Besonderheiten:
         Komplett in Python, kein externer Server notwendig.
         Modularer Aufbau für einfache Erweiterung.
         Ressourcenoptimierung integriert.
         Verbindet technische und philosophische Ansätze.
