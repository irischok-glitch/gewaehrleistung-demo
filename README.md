# Gewährleistungsantrag Prototyp – ALZURA AG

Funktionierender Prototyp für den Gewährleistungsprozess (Kundenformular + Backoffice).

## Schnellstart auf dem eigenen Server

### 1. Voraussetzungen
- Python 3.10 oder höher
- pip

### 2. Installation
```bash
cd gewaehrleistung
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Starten
```bash
# Entwicklungsmodus (zum Testen)
python3 app.py

# Oder mit Gunicorn (empfohlen für Demo)
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

Die Anwendung ist dann erreichbar unter:
- **Kundenformular:** http://<server-ip>:5000/
- **Backoffice:** http://<server-ip>:5000/backoffice

### 4. Wichtige Hinweise
- Dateien werden im Ordner `uploads/` gespeichert
- Antragsdaten in `data/claims.json`
- Für die Demo reicht der direkte Start. Für dauerhaften Betrieb später systemd oder Docker verwenden.
- Port 5000 ggf. in der Firewall freigeben.

## Funktionen im Prototyp
- Vollständiges Formular mit allen Pflichtfeldern
- Harte Upload-Gates (Ersteinbaurechnung, Kostenaufstellung, Diagnoseprotokoll)
- Automatische Dateiumbenennung und Ordnerstruktur
- Backoffice mit Statusverwaltung, Kommentaren und Chat
- Statusmodell wie abgestimmt

## Nächste Schritte nach der Demo
- Echte E-Mail-Integration
- Benutzerlogin für Mitarbeiter
- DSGVO-Dokumentation
- Migration auf Produktionsumgebung
