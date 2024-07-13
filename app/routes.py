from flask import render_template
from app import app
from .forms import LoginForm


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
    form = LoginForm()
    return render_template("login.html", title="Log In", form=form)
