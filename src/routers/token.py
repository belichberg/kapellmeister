from fastapi import APIRouter

from fastapi import APIRouter

from src.database.models import APIToken
from src.models.manager import TokenAPI

router = APIRouter()


@router.delete("/token/{token_id}/", response_model=TokenAPI)
def delete_token(token_id: int) -> TokenAPI:
    """Delete chosen token"""
    return TokenAPI.parse_obj(APIToken.delete(id=token_id).to_dict())
