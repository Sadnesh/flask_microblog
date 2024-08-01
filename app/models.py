import jwt
from time import time
from hashlib import md5
import sqlalchemy as sal
from app import db, login
from typing import Optional
import sqlalchemy.orm as sorm
from flask import current_app
from flask_login import UserMixin
from datetime import datetime, timezone
from app.search import add_to_index, remove_from_index, query_index
from werkzeug.security import generate_password_hash, check_password_hash


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(
            cls.__tablename__, expression, page, per_page  # type:ignore
        )
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        query = (
            sal.select(cls)
            .where(cls.id.in_(ids))  # type:ignore
            .order_by(db.case(*when, value=cls.id))  # type:ignore
        )
        return db.session.scalars(query), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            "add": list(session.new),
            "update": list(session.dirty),
            "delete": list(session.deleted),
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes["add"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)  # type:ignore
        for obj in session._changes["update"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)  # type:ignore
        for obj in session._changes["delete"]:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)  # type:ignore
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in db.session.scalars(sal.select(cls)):
            add_to_index(cls.__tablename__, obj)  # type:ignore


db.event.listen(db.session, "before_commit", SearchableMixin.before_commit)
db.event.listen(db.session, "after_commit", SearchableMixin.after_commit)


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

    def following_posts(self):
        Author = sorm.aliased(User)
        Follower = sorm.aliased(User)
        return (
            sal.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sal.or_(Follower.id == self.id, Author.id == self.id))
            .group_by(Post.id)
            .order_by(Post.timestamp.desc())
        )

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return
        return db.session.get(User, id)

    def __repr__(self):
        return "<User {}>".format(self.username)


class Post(SearchableMixin, db.Model):
    __searchable__ = ["body"]
    id: sorm.Mapped[int] = sorm.mapped_column(primary_key=True)
    body: sorm.Mapped[str] = sorm.mapped_column(sal.String(140))
    timestamp: sorm.Mapped[datetime] = sorm.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: sorm.Mapped[int] = sorm.mapped_column(sal.ForeignKey(User.id), index=True)
    author: sorm.Mapped[User] = sorm.relationship(back_populates="posts")
    language: sorm.Mapped[Optional[str]] = sorm.mapped_column(sal.String(5))

    def __repr__(self) -> str:
        return "<Post {}>".format(self.body)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
