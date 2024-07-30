from app import db
import sqlalchemy as sal
from app.models import User
from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from wtforms import StringField, PasswordField, BooleanField, SubmitField


class LoginForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])  # type:ignore
    password = PasswordField(_l("Password"), validators=[DataRequired()])  # type:ignore
    remember_me = BooleanField(_l("Remember Me"))  # type:ignore
    submit = SubmitField(_l("Log In"))  # type:ignore


class RegistrationForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])  # type:ignore
    email = StringField(
        _l("Email"), validators=[DataRequired(), Email()]  # type:ignore
    )
    password = PasswordField(_l("Password"), validators=[DataRequired()])  # type:ignore
    password2 = PasswordField(
        _l("Repeat Password"),  # type:ignore
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField(_l("Register"))  # type:ignore

    def validate_username(self, username):
        user = db.session.scalar(sal.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError(_("Please use a different username."))

    def validate_email(self, email):
        user = db.session.scalar(sal.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError(_("Please use a different email address."))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        _l("Email"), validators=[DataRequired(), Email()]  # type:ignore
    )
    submit = SubmitField(_l("Request password reset"))  # type:ignore


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l("Password"), validators=[DataRequired()])  # type:ignore
    password2 = PasswordField(
        _l("Repeat Password"),  # type:ignore
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField(_l("Reset password"))  # type:ignore
