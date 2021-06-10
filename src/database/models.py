from sqlalchemy import Column, Integer, VARCHAR, Text, ForeignKey, String, JSON, Boolean, Enum, Table, TIMESTAMP, func
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from src.database.helpers import ModelMixin
from src.models.user import UserRole

Base: DeclarativeMeta = declarative_base()

user_project_table = Table('user_project', Base.metadata,
                           Column('user_id', Integer, ForeignKey('users.id')),
                           Column('project_id', Integer, ForeignKey('projects.id'))
                           )


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
    updated_time = Column("updated_time", TIMESTAMP, server_default=func.now(), nullable=False)
    # updated_time = Column("updated_time", TIMESTAMP, default=time(), nullable=False)
    project_id = Column("project_id", Integer, ForeignKey("projects.id"), nullable=True)
    channel_id = Column("channel_id", Integer, ForeignKey("channels.id"), nullable=True)

    def to_dict(self):
        return dict(
            id=self.id,
            slug=self.slug,
            auth=self.auth,
            digest=self.digest,
            parameters=self.parameters,
            updated_time=self.updated_time,
            project_id=self.project_id,
            channel_id=self.channel_id,
        )


class APIToken(ModelMixin, Base):
    __tablename__ = "tokens"

    id = Column("id", Integer, nullable=False, primary_key=True, index=True, unique=True)
    token = Column("token", VARCHAR(64), nullable=False, unique=True)
    read_only = Column("read_only", Boolean, nullable=False)
    project_id = Column("project_id", Integer, ForeignKey("projects.id"), nullable=True)

    def to_dict(self):
        return dict(id=self.id, token=self.token, read_only=self.read_only, project_id=self.project_id)


class User(ModelMixin, Base):
    __tablename__ = "users"

    id = Column("id", Integer, nullable=False, primary_key=True, index=True, unique=True)
    username = Column("username", VARCHAR(64), nullable=False, unique=True)
    password = Column("password", VARCHAR(64), nullable=False)
    role = Column('role', Enum(UserRole), nullable=False, default=UserRole.user)
    is_active = Column("is_active", Boolean, nullable=False, default=True)

    # children = relationship("Child",
    #                         secondary=user_project_table)

    def to_dict(self):
        return dict(
            id=self.id, username=self.username, password=self.password, role=self.role, is_active=self.is_active
        )
