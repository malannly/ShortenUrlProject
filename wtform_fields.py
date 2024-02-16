from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from models_db import User
from create_eng import get_connection
from sqlalchemy import select
from passlib.hash import pbkdf2_sha256

def invalid_credentials(form, field):
    username_entered = form.username.data
    password_entered = field.data
    engine = get_connection()
    with engine.connect() as connection:
        query = select([User]).where(User.c.username == username_entered)
        user_object = query.execute().fetchone()
    if user_object is None:
        raise ValidationError('Username or password is incorrect.')
    elif not pbkdf2_sha256.verify(password_entered, user_object.password):
        raise ValidationError('Username or password is incorrect.')

class RegistrationForm(FlaskForm):
    username = StringField('username_label', validators = [
    InputRequired(message = 'Username required'),
    Length(min = 3, max = 29, message = 'Username must be between 3 and 29 characters')])
    password = PasswordField('password_label', validators = [
    InputRequired(message = 'Password required'),
    Length(min = 7, max = 15, message = 'Password must be between 7 and 15 characters')])
    confirm_pswd = PasswordField('confirm_pswd_label', validators = [
    InputRequired(message = 'Password required'),
    EqualTo('password', message = 'Password must match')])
    submit_button = SubmitField('Create')

    def validate_username(self,username):
            engine = get_connection()
            with engine.connect() as connection:
                query = select([User]).where(User.c.username == username.data) # check if the username has already existed
                user_object = query.execute().fetchone()
            if user_object:
                raise ValidationError('This username already exists. Select another username.')

class LoginForm(FlaskForm):
    username = StringField('username_label', validators = [
    InputRequired(message = 'Username required')
    ])
    password = PasswordField('password_label', validators = [
    InputRequired(message = 'Password required'),
    invalid_credentials
    ])
    submit_button = SubmitField('Login')