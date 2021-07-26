from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from src.database.models import APIKey, UserRole
from src.dependencies import get_user, generate_api_token
from src.models.manager import APIKeyModel, APIKeyRequestModel
from src.models.user import UserAPI

router = APIRouter(
    prefix="/keys",
    tags=["keys"],
)


@router.get("/", response_model=List[APIKeyModel])
async def get_keys(user: Optional[UserAPI] = Depends(get_user)) -> List[APIKeyModel]:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    return [APIKeyModel.parse_obj(token.to_dict()) for token in APIKey.get_all()]


@router.post("/", response_model=APIKeyModel)
async def create_key(data: APIKeyRequestModel, user: Optional[UserAPI] = Depends(get_user)) -> APIKeyModel:
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    # Generating a random string for the token
    data.token = generate_api_token()

    return APIKeyModel.parse_obj(APIKey.create(data.dict()).to_dict())


@router.patch("/{key_id}/", response_model=APIKeyModel)
async def update_key(key_id: int, data: APIKeyRequestModel, user: Optional[UserAPI] = Depends(get_user)) -> APIKeyModel:
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    return APIKeyModel.parse_obj(APIKey.update(data.dict(), id=key_id).to_dict())


@router.delete("/{key_id}/", response_model=APIKeyModel)
async def delete_token(key_id: int, user: Optional[UserAPI] = Depends(get_user)) -> APIKeyModel:
    """Delete chosen token"""
    if user is None or user.role != UserRole.super:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Token"},
        )

    return APIKeyModel.parse_obj(APIKey.delete(id=key_id).to_dict())
