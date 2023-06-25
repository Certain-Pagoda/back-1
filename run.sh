#!/bin/sh

uvicorn "app:app"  --forwarded-allow-ips \* --port 8080 --reload
