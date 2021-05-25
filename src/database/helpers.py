from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, Query

from src.models.manager import ContainerAPI


class ModelMixin(object):
    @classmethod
    def create(cls, session: Session, body: Dict):
        try:
            # Create an object in the database
            obj = cls(**body)
            session.add(obj)
            session.commit()
            session.refresh(obj)

            return obj
        except SQLAlchemyError as err:
            print("Database error:", err)

        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def get(cls, session: Session, slug: str) -> Query:
        obj: Query = session.query(cls).filter_by(slug=slug)
        if obj.first():
            return obj

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    @classmethod
    def update(cls, session: Session, slug: str, body: Dict) -> Query:
        obj: Query = cls.get(session, slug).first()
        cls.update_obj(session, obj, body)

        return obj

    @classmethod
    def update_or_create(cls, session: Session, body: ContainerAPI):
        try:
            obj = (
                cls.get(session, body.slug)
                .filter_by(project_id=body.project_id)
                .filter_by(channel_id=body.channel_id)
                .first()
            )
            cls.update_obj(session, obj, body.dict())
        except HTTPException as err:
            if err.status_code != 404:
                raise err
            obj = cls.create(session, body.dict())

        return obj

    @classmethod
    def update_obj(cls, session: Session, obj: Query, body: Dict) -> Query:
        try:
            for key, value in body.items():
                setattr(obj, key, value)

            session.commit()

        except SQLAlchemyError as err:
            print("Database error:", err)

        return obj

    # @classmethod
    # def delete(cls, session: Session, slug: str) -> Query:
    #     obj: Query = cls.get(session, slug).first()
    #     session.delete(obj)
    #     session.commit()
    #
    #     return obj
