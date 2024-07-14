import sqlalchemy as sal
import sqlalchemy.orm as sorm
from app import app, db
from app.models import User, Post


@app.shell_context_processor
def make_shell_context():
    return {"sal": sal, "sorm": sorm, "db": db, "User": User, "Post": Post}
