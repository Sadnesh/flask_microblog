from hashlib import md5
import sqlalchemy as sal
from app import db, login
from typing import Optional
import sqlalchemy.orm as sorm
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

followers = sal.Table(
    "followers",
    db.metadata,
    sal.Column("follower_id", sal.Integer, sal.ForeignKey("user.id"), primary_key=True),
    sal.Column("followed_id", sal.Integer, sal.ForeignKey("user.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    id: sorm.Mapped[int] = sorm.mapped_column(primary_key=True)
    username: sorm.Mapped[str] = sorm.mapped_column(
        sal.String(64), index=True, unique=True
    )
    email: sorm.Mapped[str] = sorm.mapped_column(
        sal.String(120), index=True, unique=True
    )
    password_hash: sorm.Mapped[Optional[str]] = sorm.mapped_column(sal.String(256))
    posts: sorm.WriteOnlyMapped["Post"] = sorm.relationship(back_populates="author")
    about_me: sorm.Mapped[Optional[str]] = sorm.mapped_column(sal.String(140))
    last_seen: sorm.Mapped[Optional[datetime]] = sorm.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    following: sorm.WriteOnlyMapped["User"] = sorm.relationship(
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates="followers",
    )
    followers: sorm.WriteOnlyMapped["User"] = sorm.relationship(
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates="following",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def following_count(self):
        query = sal.select(sal.func.count()).select_from(
            self.following.select().subquery()
        )
        return db.session.scalar(query)

    def followers_count(self):
        query = sal.select(sal.func.count()).select_from(
            self.followers.select().subquery()
        )
        return db.session.scalar(query)

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


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
