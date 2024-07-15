from app import app, db
import sqlalchemy as sal
from app.models import User
from .forms import LoginForm
from flask_login import current_user, login_user, logout_user
from flask import render_template, flash, redirect, url_for


@app.route("/")
@app.route("/index")
def index():
    user = {"username": "Sadnesh"}
    posts = [
        {"author": {"username": "someone"}, "body": "It's a wonderful day"},
        {"author": {"username": "noone"}, "body": "It's a shitty day"},
        {"author": {"username": "somebody"}, "body": "It's a joyful today"},
    ]
    return render_template("index.html", title="Blog Testing", user=user, posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sal.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid Username or Password!")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("index"))

    return render_template("login.html", title="Log In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
