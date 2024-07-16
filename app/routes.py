from app import app, db
import sqlalchemy as sal
from app.models import User
from .forms import LoginForm
from urllib.parse import urlsplit
from app.forms import RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request


@app.route("/")
@app.route("/index")
@login_required
def index():
    posts = [
        {"author": {"username": "someone"}, "body": "It's a wonderful day"},
        {"author": {"username": "noone"}, "body": "It's a shitty day"},
        {"author": {"username": "somebody"}, "body": "It's a joyful today"},
    ]
    return render_template("index.html", title="Blog Testing", posts=posts)


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
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)

    return render_template("login.html", title="Log In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congrats, you're now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)
