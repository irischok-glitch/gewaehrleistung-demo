#!/bin/bash
# Einfacher Startskript für den Prototyp

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Erstelle virtuelle Umgebung..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q

echo "Starte Gewährleistungs-Prototyp auf Port 5000..."
echo "Kundenformular: http://$(hostname -I | awk '{print $1}'):5000/"
echo "Backoffice:     http://$(hostname -I | awk '{print $1}'):5000/backoffice"
echo ""
echo "Zum Beenden: Ctrl+C"

gunicorn -w 2 -b 0.0.0.0:5000 app:app
