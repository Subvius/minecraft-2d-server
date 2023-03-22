import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Guild(SqlAlchemyBase):
    __tablename__ = 'guilds'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True, index=True)
    desc = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,
                                   default=datetime.datetime.now)
    updated_at = sqlalchemy.Column(sqlalchemy.DateTime,
                                   default=datetime.datetime.now)
    members = sqlalchemy.Column(sqlalchemy.PickleType, default={})
    gexp = sqlalchemy.Column(sqlalchemy.PickleType, default={})
    owner_uuid = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.uuid"))

    owner = orm.relationship("User")
