from typing import Dict

from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session


def get_db(request: Request):
    return request.state.db


class ModelMixin(object):
    @classmethod
    def create(cls, body: Dict, db: Session):
        obj = cls(**body)
        db.add(obj)
        db.commit()
        db.refresh(obj)

        return obj

    @classmethod
    def get(cls, slug: str, db: Session):
        obj = db.query(cls).filter_by(slug=slug)
        if obj:
            return obj

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
