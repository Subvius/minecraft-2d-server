import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    nickname: str = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True, index=True)
    first_login = sqlalchemy.Column(sqlalchemy.DateTime,
                                    default=datetime.datetime.now)
    last_login = sqlalchemy.Column(sqlalchemy.DateTime,
                                   default=datetime.datetime.now)
    last_logout = sqlalchemy.Column(sqlalchemy.DateTime,
                                    default=datetime.datetime.now)
    uuid: str = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True, nullable=False)
    cloak: str = sqlalchemy.Column(sqlalchemy.String, default="")
    password: str = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    skin_uuid: str = sqlalchemy.Column(sqlalchemy.String)
    reputation: dict = sqlalchemy.Column(sqlalchemy.PickleType, nullable=False, default={
        "killer": 150,
        "magician": 150,
        "robber": 150,
        "smuggler": 150,
        "spice": 150
    })
    cosmetics: dict = sqlalchemy.Column(sqlalchemy.PickleType, default={})
    active_tasks: dict = sqlalchemy.Column(sqlalchemy.PickleType, default={})
    stats: dict = sqlalchemy.Column(sqlalchemy.PickleType, default={"play_time": 0})

    def jsonify(self) -> dict:
        return {
            "nickname": self.nickname,
            "first_login": self.first_login,
            "last_login": self.last_login,
            "last_logout": self.last_logout,
            "uuid": self.uuid,
            "cloak": self.cloak,
            "skin_uuid": self.skin_uuid,
            "reputation": self.reputation,
            "cosmetics": self.cosmetics,
            "active_tasks": self.active_tasks,
            "stats": self.stats,
        }
