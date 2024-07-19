from app import app, db
import sqlalchemy as sal
from app.models import User
from urllib.parse import urlsplit
from datetime import datetime, timezone
from .forms import LoginForm, RegistrationForm, EditProfileForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required


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


@app.route("/user/<username>")
@login_required
def user(username: str):
    user = db.first_or_404(sal.select(User).where(User.username == username))
    name = user.username
    posts = [
        {"author": {"username": f"{name}"}, "body": "k xa soltini"},
        {"author": {"username": f"{name}"}, "body": "hoina nani ramri paltera kata"},
        {"author": {"username": f"{name}"}, "body": "i sometimes think i am a creep"},
    ]
    return render_template("user.html", user=user, posts=posts)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved")
        return redirect(url_for("edit_profile"))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template("edit_profile.html", title="Edit profile", form=form)
