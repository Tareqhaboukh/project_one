from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateTimeField
from wtforms.validators import DataRequired, Email

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Edit User')

class LogInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Login")

class ChangePassword(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Change Password")

class CheckPassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Check Password")

class ResetPassword(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    submit = SubmitField("Reset Password")