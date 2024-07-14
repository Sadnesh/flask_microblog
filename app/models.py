from app import db
import sqlalchemy as sal
from typing import Optional
import sqlalchemy.orm as sorm
from datetime import datetime, timezone


class User(db.Model):
    id: sorm.Mapped[int] = sorm.mapped_column(primary_key=True)
    username: sorm.Mapped[str] = sorm.mapped_column(
        sal.String(64), index=True, unique=True
    )
    email: sorm.Mapped[str] = sorm.mapped_column(
        sal.String(120), index=True, unique=True
    )
    password_hash: sorm.Mapped[Optional[str]] = sorm.mapped_column(sal.String(256))
    posts: sorm.WriteOnlyMapped["Post"] = sorm.relationship(back_populates="author")

    def __repr__(self):
        return "<User {}>".format(self.username)


class Post(db.Model):
    id: sorm.Mapped[int] = sorm.mapped_column(primary_key=True)
    body: sorm.Mapped[str] = sorm.mapped_column(sal.String(140))
    timestamp: sorm.Mapped[datetime] = sorm.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: sorm.Mapped[int] = sorm.mapped_column(sal.ForeignKey(User.id), index=True)
    author: sorm.Mapped[User] = sorm.relationship(back_populates="posts")

    def __repr__(self) -> str:
        return "<Post {}>".format(self.body)
