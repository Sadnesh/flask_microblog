from app import db
import sqlalchemy as sal
from app.models import User
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from wtforms import StringField, PasswordField, BooleanField, SubmitField


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")


    def validate_username(self,username):
        user=db.session.scalar(sal.select(User).where(User.username==username.data))
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self,email):
        user=db.session.scalar(sal.select(User).where(User.email==email.data))
        if user is not None:
            raise ValidationError("Please use a different email address.")