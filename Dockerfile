FROM python:3.10-slim

WORKDIR /app

# Copie et installe les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code de ton bot
COPY . .

# Lance le bot
CMD ["python", "bot.py"]
