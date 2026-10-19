# Image du serveur (API + WebSocket). Construite depuis le dossier backend/.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GTN_DB_PATH=/data/main.db

WORKDIR /app

# dependances d'abord (cache de build), code ensuite
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# utilisateur sans droits particuliers; /data accueille la base (volume persistant monte par l'hebergeur)
RUN useradd --create-home app && mkdir -p /data && chown -R app:app /app /data
USER app

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import os,sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:%s/health' % os.environ.get('PORT', '8080'), timeout=4).status == 200 else 1)"

# UN SEUL processus: la limitation de debit et les connexions WebSocket sont gardees en memoire
# $PORT: le port impose par l'hebergeur (Render); 8080 par defaut (Fly, local)
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
