from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, Query

from src.database import SessionLocal

session: Session = SessionLocal()


class ModelMixin(object):
    @classmethod
    def create(cls, body: Dict):
        try:
            # Create an object in the database
            obj: cls = cls(**body)
            session.add(obj)
            session.commit()
            session.refresh(obj)

            return obj
        except SQLAlchemyError as err:
            print("Database error:", err)

        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def get(cls, **kwargs):
        obj: cls = session.query(cls).filter_by(**kwargs).first()
        return obj
        # if obj:
        #     return obj
        #
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    @classmethod
    def get_all(cls, **kwargs) -> Query:
        obj: Query = session.query(cls).filter_by(**kwargs)
        # if obj.first():
        return obj

        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    @classmethod
    def get_or_create(cls, body: Dict, **kwargs):
        obj: cls = cls.get(**kwargs)
        if obj is None:
            obj: cls = cls.create(body)

        return obj

    @classmethod
    def update(cls, body: Dict, **kwargs):
        obj: cls = cls.get(**kwargs)
        cls.update_obj(obj, body)

        return obj

    @classmethod
    def update_or_create(cls, body: Dict, **kwargs):
        obj: cls = cls.get(**kwargs)
        if obj:
            obj: cls = cls.update_obj(obj, body)
        else:
            obj: cls = cls.create(body)

        return obj

    @classmethod
    def update_obj(cls, obj, body: Dict):
        try:
            for key, value in body.items():
                setattr(obj, key, value)

            session.commit()

        except SQLAlchemyError as err:
            print("Database error:", err)

        return obj

    @classmethod
    def delete(cls, **kwargs):
        obj: cls = cls.get(**kwargs)
        session.delete(obj)
        session.commit()

        return obj

    @classmethod
    def delete_all(cls, **kwargs):
        objs: Query = cls.get_all(**kwargs)
        remote = []
        for obj in objs:
            session.delete(obj)
            session.commit()
            remote.append(obj)

        return remote
