# Deployment auf Render.com (kostenfrei für Demo)

## Schritte

1. Repository auf GitHub pushen (oder manuell hochladen)
2. Auf render.com neuen Web Service erstellen
3. Umgebungsvariablen setzen:
   - `SMTP_SERVER` = smtp.office365.com (oder euer Mailserver)
   - `SMTP_PORT` = 587
   - `SMTP_USER` = irina.wuckert@alzura.com
   - `SMTP_PASSWORD` = (Passwort der Adresse)
   - `FROM_EMAIL` = irina.wuckert@alzura.com
   - `SECRET_KEY` = beliebiger langer String

4. Start Command: `gunicorn app:app`

## Hinweise
- Ohne SMTP_PASSWORD werden E-Mails nur geloggt, nicht gesendet
- Dateien werden im `uploads/` Ordner gespeichert
- Free-Tier auf Render: App schläft nach Inaktivität

## Testen
- Formular: https://<deine-app>.onrender.com/
- Backoffice: https://<deine-app>.onrender.com/backoffice
