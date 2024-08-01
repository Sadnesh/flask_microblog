from flask_wtf.form import _Auto
from app import db
import sqlalchemy as sal
from flask import request
from app.models import User
from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms.validators import DataRequired, ValidationError, Length
from wtforms import StringField, SubmitField, TextAreaField


class PostForm(FlaskForm):
    post = TextAreaField(
        _l("What's in your mind today..."),  # type:ignore
        validators=[DataRequired(), Length(min=1, max=140)],
    )
    submit = SubmitField(_l("Submit"))  # type:ignore


class EditProfileForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])  # type:ignore
    about_me = TextAreaField(
        _l("About me"), validators=[Length(min=0, max=140)]  # type:ignore
    )
    submit = SubmitField(_l("Submit"))  # type:ignore

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(
                sal.select(User).where(User.username == username.data)
            )
            if user is not None:
                raise ValidationError(_("Please use a different username"))


# For follow and unfollow actions
class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    q = StringField(_l("Search"), validators=[DataRequired()])  # type:ignore

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "meta" not in kwargs:
            kwargs["meta"] = {"csrf": False}
        super(SearchForm, self).__init__(*args, **kwargs)
