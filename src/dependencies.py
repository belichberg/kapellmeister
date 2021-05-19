# from sqlalchemy.orm import Session
# from src.database.models import Container
# from src.models.manager import ContainerAPI
#
#
# def create_container(db: Session, item: ContainerAPI):
#     container = Container(**item.dict())
#     db.add(container)
#     db.commit()
#     db.refresh(container)
#
#     return container
