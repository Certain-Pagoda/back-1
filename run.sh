#!/bin/sh

uvicorn "app:app" --host 0.0.0.0  --port 8080 --reload
#gunicorn --bind :8080 --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 1 app:app --reload
