from sqlalchemy import Column, Integer, VARCHAR, Text, ForeignKey, String

from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import relationship

Base: DeclarativeMeta = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column('id', Integer, nullable=False, primary_key=True, index=True, unique=True)
    name = Column('name', VARCHAR(64), nullable=False)
    slug = Column('slug', VARCHAR(64), nullable=False, unique=True)
    description = Column('description', Text(512), nullable=False)


class Channel(Base):
    __tablename__ = "channels"

    id = Column('id', Integer, nullable=False, primary_key=True, index=True, unique=True)
    name = Column('name', VARCHAR(64), nullable=False)
    slug = Column('slug', VARCHAR(64), nullable=False)
    description = Column('description', Text(512), nullable=False)
    project_id = Column('project_id', Integer, ForeignKey('projects.id'), nullable=True)


class Container(Base):
    __tablename__ = "containers"

    id = Column('id', Integer, nullable=False, primary_key=True, index=True, unique=True)
    slug = Column('slug', VARCHAR(64), nullable=False)
    auth = Column('auth', String(2000), nullable=True)
    hash = Column('hash', VARCHAR(255), nullable=False)
    parameters = Column('parameters', String(2000), nullable=False)
    project_id = Column('project_id', Integer, ForeignKey('projects.id'), nullable=True)
    # project = relationship("Project")
    channel_id = Column('channel_id', Integer, ForeignKey('channels.id'), nullable=True)
    # channel = relationship("Channel")
