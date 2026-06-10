# Basis-Image
FROM python:3.11-slim

# Flask installieren
RUN pip install flask

# Arbeitsverzeichnis
WORKDIR /app

# Dateien in Container kopieren
COPY flaskServer.py /app/
COPY templates/ /app/templates/

# Port freigeben
EXPOSE 5000

# Startbefehl
CMD ["python", "flaskServer.py"]