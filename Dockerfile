# Utilise une image Python 3.10 officielle
FROM python:3.10-slim

# Définit le dossier de travail
WORKDIR /app

# Copie et installe les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code
COPY . .

# Expose le port 10000 pour Flask
EXPOSE 10000

# Lance le bot
CMD ["python", "bot.py"]
