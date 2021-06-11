from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from src.database.models import User, APIToken
from src.dependencies import time_utc_now, pwd_verify, JWT_TOKEN_EXPIRE, token_create, JWT_KEY, JWT_ALGORITHM
from src.models.manager import TokenAPI
from src.models.user import UserAPI, TokenData, JWTToken

router = APIRouter()


@router.delete("/token/{token_id}/", response_model=TokenAPI)
def delete_token(token_id: int) -> TokenAPI:
    """Delete chosen token"""
    return TokenAPI.parse_obj(APIToken.delete(id=token_id).to_dict())
