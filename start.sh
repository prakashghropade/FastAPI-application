#!/bin/sh

# Exit immediately if any command returns a non-zero exit code
set -e

echo "Waiting for PostgreSQL database connection..."

# Python script to check if the database port is active
python -c "
import socket
import time
import os
from urllib.parse import urlparse

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print('DATABASE_URL is not set, skipping health check.')
    exit(0)

url = urlparse(db_url)
host = url.hostname
port = url.port if url.port else 5432

print(f'Probing database connection at {host}:{port}...')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2.0)
while True:
    try:
        s.connect((host, int(port)))
        s.close()
        print('PostgreSQL is available!')
        break
    except (socket.error, socket.timeout):
        print('PostgreSQL port not ready yet, retrying in 1 second...')
        time.sleep(1)
"

echo "Applying Alembic database migrations..."
alembic upgrade head

echo "Starting FastAPI Uvicorn production server..."
# Using exec to run the uvicorn process as PID 1 (captures SIGTERM/SIGINT signals properly for graceful shutdown)
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers --forwarded-allow-ips='*'
