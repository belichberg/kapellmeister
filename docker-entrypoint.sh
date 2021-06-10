#!/bin/bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
gunicorn --workers 4 --access-logfile - --log-level debug -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app