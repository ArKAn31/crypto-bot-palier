FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Commande de démarrage du bot en polling
CMD ["python", "bot.py"]

