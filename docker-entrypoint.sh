#!/bin/bash
set -e

if [[ "$1" = "entry" ]]; then
    # run python
    exec sh -c "alembic upgrade head && gunicorn --workers 4 --access-logfile - --log-level debug -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app"

elif [[ "$1" = "tests" ]]; then
    # run test
    exec /usr/local/bin/python -u -m pytest -v -p no:warnings --cov

else
    # run by default
    exec "$@"
fi

