from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from src.database.models import APIToken, UserRole
from src.dependencies import get_user, generate_api_token
from src.models.manager import TokenAPI, TokenRequestAPI
from src.models.user import UserAPI

router = APIRouter()


@router.get("/tokens/", response_model=List[TokenAPI])
def get_tokens(user: Optional[UserAPI] = Depends(get_user)) -> List[TokenAPI]:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    return [TokenAPI.parse_obj(token.to_dict()) for token in APIToken.get_all()]


@router.post("/tokens/", response_model=TokenAPI)
def create_token(
    read_only: bool = True, project: Optional[int] = None, user: Optional[UserAPI] = Depends(get_user)
) -> TokenAPI:
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    data = dict(token=generate_api_token(), read_only=read_only, project_id=project)
    return TokenAPI.parse_obj(APIToken.create(data).to_dict())


@router.patch("/tokens/{token_id}/", response_model=TokenAPI)
def update_token(token_id: int, data: TokenRequestAPI, user: Optional[UserAPI] = Depends(get_user)) -> TokenAPI:
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    return TokenAPI.parse_obj(APIToken.update(data.dict(), id=token_id).to_dict())


@router.delete("/tokens/{token_id}/", response_model=TokenAPI)
def delete_token(token_id: int, user: Optional[UserAPI] = Depends(get_user)) -> TokenAPI:
    """Delete chosen token"""
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    return TokenAPI.parse_obj(APIToken.delete(id=token_id).to_dict())
