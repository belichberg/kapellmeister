import secrets
import string
from datetime import datetime, timezone

from fastapi import Request


def time_utc_now(timestamp: int = None) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else datetime.now(tz=timezone.utc)


def get_db(request: Request):
    return request.state.db


def generate_token():
    return str(''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(40)))
