Love Yourself

Love Yourself ist eine personalisierte Webanwendung rund um Ernährung, Fitness und persönlichen Fortschritt.
Die Anwendung verbindet klassische Webentwicklung mit künstlicher Intelligenz, um individuelle Ernährungs- und Fitnesspläne auf Basis von Nutzerdaten, Zielen, Vorlieben und Feedback zu erstellen.

Hinweis: Das Projekt wurde als Schul-/Lernprojekt entwickelt und ersetzt keine medizinische, ernährungswissenschaftliche oder sportmedizinische Beratung.

Funktionen

Benutzerprofil

Im Profil werden die Informationen gespeichert, die für die Personalisierung benötigt werden, zum Beispiel:

Alter, Größe und Gewicht

Zielgewicht und Aktivitätslevel

Ernährungsform und Allergien

bevorzugte und unerwünschte Lebensmittel

Fitnesslevel und Trainingstage

vorhandenes Equipment

bevorzugte und unerwünschte Übungen

persönliche Wünsche und Notizen

KI-generierte Ernährungspläne

Die Anwendung erstellt individuelle Ernährungspläne auf Grundlage der gespeicherten Profildaten.

Enthalten sind unter anderem:

7-Tage-Ernährungsplan

Kalorienziel

Mahlzeiten

Zutaten

Zubereitungsanleitungen

automatisch generierte Einkaufsliste

Berücksichtigung von Allergien und Vorlieben

KI-generierte Fitnesspläne

Für den Fitnessbereich werden personalisierte Trainingspläne erstellt.

Berücksichtigt werden unter anderem:

Fitnesslevel

Anzahl der Trainingstage

Trainingspräferenzen

vorhandenes Equipment

bevorzugte und unerwünschte Übungen

individuelle Wünsche

Die Übungen enthalten zusätzlich konkrete Anleitungen.

Fortschritt

Der Nutzer kann sein Gewicht regelmäßig eintragen und seine Entwicklung verfolgen.

Feedback & Personalisierung

Mahlzeiten und Übungen können mit positivem oder negativem Feedback bewertet werden.
Zusätzlich kann Feedback zu einem gesamten Plan gespeichert, geändert oder gelöscht werden.

Dieses Feedback wird bei zukünftigen Planerstellungen berücksichtigt und ermöglicht dadurch eine stärkere Personalisierung.

PDF-Export

Erstellte Inhalte können als PDF exportiert werden, zum Beispiel:

Ernährungsplan

Einkaufsliste

Fitnessplan

Community

Die Anwendung enthält außerdem einen Community-Bereich mit:

Beiträgen

Kommentaren

Likes

Bildern

KI-Ablauf

Die KI ist in einen festen Programmablauf eingebunden:

Nutzerdaten werden aus der Datenbank geladen.

Eine im Code hinterlegte Prompt-Vorlage wird geladen.

Die relevanten Profildaten, Präferenzen und Feedbackinformationen werden in den Prompt eingesetzt.

Die Anfrage wird über die OpenAI API an das KI-Modell gesendet.

Die Antwort wird strukturiert zurückgegeben.

Pydantic prüft die Antwort anhand definierter Schemas.

Der fertige Plan wird in der Datenbank gespeichert.

Die Anwendung stellt die Inhalte im Browser dar.

Neues Feedback kann bei späteren Plänen erneut berücksichtigt werden.

Dadurch übernimmt die KI nur die eigentliche Generierung der Inhalte.
Das Laden der Daten, die Prompt-Erstellung, Validierung, Speicherung und Darstellung werden durch die Anwendung gesteuert.

Technologien

Backend

Python

Flask

Flask-SQLAlchemy

SQLite

Frontend

HTML

Jinja

CSS

Künstliche Intelligenz

OpenAI API

Structured Outputs

Pydantic

PDF-Erstellung

ReportLab

Tests

pytest

pytest-cov

Projektstruktur

Love_yourself/
│
├── routes/          # Seitenaufrufe und Benutzeranfragen
├── services/        # Programmlogik, KI, Feedback und Planerstellung
├── models/          # SQLAlchemy-Datenbankmodelle
├── schemas/         # Pydantic-Schemas für strukturierte KI-Antworten
├── templates/       # HTML- und Jinja-Templates
├── static/          # CSS, Bilder und Uploads
├── pdf/             # PDF-Erstellung mit ReportLab
├── utils/           # Hilfsfunktionen und Validierungen
├── tests/           # Automatisierte Tests
│
├── app.py            # Einstiegspunkt der Flask-Anwendung
├── config.py         # Anwendungskonfiguration
├── extensions.py     # Flask-Erweiterungen
└── requirements.txt  # Python-Abhängigkeiten

Datenbank

Die Anwendung verwendet SQLite zusammen mit SQLAlchemy.

Zu den wichtigsten Tabellen gehören:

user

profile

weight_entry

plan

plan_feedback

meal_preference

exercise_preference

Zusätzlich existieren Tabellen für Community- und Support-Funktionen.

Ein Benutzer besitzt genau ein Profil, kann aber mehrere Gewichtseinträge, Pläne und Feedbackeinträge besitzen.

Installation

1. Repository klonen

git clone <DEINE-GITHUB-REPOSITORY-URL>
cd Love_yourself

2. Virtuelle Umgebung erstellen

Windows:

python -m venv .venv
.venv\Scripts\activate

macOS / Linux:

python3 -m venv .venv
source .venv/bin/activate

3. Abhängigkeiten installieren

pip install -r requirements.txt

Die Anwendung verwendet außerdem die Pakete openai und pydantic.
Falls diese noch nicht über die Requirements installiert werden, können sie zusätzlich installiert werden:

pip install openai pydantic

Umgebungsvariablen

Im Projektverzeichnis wird eine .env-Datei benötigt.

Beispiel:

OPENAI_API_KEY=dein_api_key
FLASK_SECRET_KEY=dein_geheimer_flask_key
ADMIN_USERNAME=admin

Die .env-Datei darf nicht auf GitHub hochgeladen werden.
Sie ist bereits über .gitignore ausgeschlossen.

Anwendung starten

python app.py

Danach ist die Anwendung standardmäßig unter folgender Adresse erreichbar:

http://127.0.0.1:5000

Beim ersten Start werden die benötigten Datenbanktabellen automatisch erstellt.

Tests ausführen

Alle Tests:

pytest

Tests mit Coverage:

pytest --cov

Im Projekt existieren unter anderem Tests für:

KI-Validierung

Profilverarbeitung

Gewichtsdaten

Routen

Validatoren

Health-/Berechnungslogik

Sicherheit

Sensible Informationen wie API-Keys werden nicht direkt im Quellcode gespeichert, sondern über Umgebungsvariablen geladen.

Folgende Dateien und Ordner werden nicht versioniert:

.env
.venv/
__pycache__/
instance/
generated_pdfs/
*.pdf

Mögliche Weiterentwicklungen

Geplante oder denkbare Erweiterungen sind:

erweiterte Auswertung des Fortschritts

stärkere Personalisierung der Pläne

zusätzliche Fitness- und Ernährungsoptionen

Verbesserung der KI-Validierung

Aufbau eines eigenen Fitnesskatalogs

Entwicklung einer mobilen App

Weiterentwicklung der Software-Architektur

Ziel des Projekts

Ziel von Love Yourself ist es, Ernährung, Fitness, Fortschritt und künstliche Intelligenz in einer Anwendung zu verbinden.

Das Projekt zeigt insbesondere, wie KI nicht nur als Chatfunktion eingesetzt werden kann, sondern als Bestandteil eines strukturierten Softwareprozesses mit:

gespeicherten Nutzerdaten

dynamischen Prompts

strukturierten Antworten

Validierung

Datenbankanbindung

langfristigem Nutzerfeedback

Autorin

Patricia Eva Nogowski