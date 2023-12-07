from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import InputRequired, ValidationError


class NewUserForm(FlaskForm):
    def validate_name(form, field):
        if len(field.data) > 20:
            raise ValidationError("Username must be less than 20 characters")

    username = StringField("Username", validators=[InputRequired(), validate_name])
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired()])


class LoginUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
