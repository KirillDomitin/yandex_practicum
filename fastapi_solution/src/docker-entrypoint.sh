#!/bin/bash
echo $FASTAPI_HOST
gunicorn -b $FASTAPI_HOST:8000 -k uvicorn.workers.UvicornWorker main:app