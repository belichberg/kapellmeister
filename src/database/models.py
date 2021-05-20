from sqlalchemy import Column, Integer, VARCHAR, Text, ForeignKey, String, JSON
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from src.helpers import ModelMixin

Base: DeclarativeMeta = declarative_base()


class Project(ModelMixin, Base):
    __tablename__ = "projects"

    id = Column("id", Integer, nullable=False, primary_key=True, index=True, unique=True)
    name = Column("name", VARCHAR(64), nullable=False)
    slug = Column("slug", VARCHAR(64), nullable=False, unique=True)
    description = Column("description", Text(512), nullable=True)

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            slug=self.slug,
            description=self.description,
        )


class Channel(ModelMixin, Base):
    __tablename__ = "channels"

    id = Column("id", Integer, nullable=False, primary_key=True, index=True, unique=True)
    name = Column("name", VARCHAR(64), nullable=False)
    slug = Column("slug", VARCHAR(64), nullable=False)
    description = Column("description", Text(512), nullable=True)
    project_id = Column("project_id", Integer, ForeignKey("projects.id"))

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            slug=self.slug,
            description=self.description,
            project_id=self.project_id,
        )


class Container(ModelMixin, Base):
    __tablename__ = "containers"

    id = Column("id", Integer, nullable=False, primary_key=True, index=True, unique=True)
    slug = Column("slug", VARCHAR(64), nullable=False)
    auth = Column("auth", String(2000), nullable=True)
    digest = Column("hash", VARCHAR(255), nullable=False)
    parameters = Column("parameters", JSON, nullable=False)
    project_id = Column("project_id", Integer, ForeignKey("projects.id"), nullable=True)
    channel_id = Column("channel_id", Integer, ForeignKey("channels.id"), nullable=True)

    def to_dict(self):
        return dict(
            id=self.id,
            slug=self.slug,
            auth=self.auth,
            digest=self.digest,
            parameters=self.parameters,
            project_id=self.project_id,
            channel_id=self.channel_id,
        )
