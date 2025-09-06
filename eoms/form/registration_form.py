# Import FlaskForm instead of the basic Form
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, validators, EmailField
from eoms.model.auth import email_exists
import re
from markupsafe import Markup

# Using regular expressions for more detailed email format validation
class EmailValidator(object):
    def __init__(self, message=None):
        if not message:
            message = u'Invalid email address.'
        self.message = message

    def __call__(self, form, field):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, field.data):
            raise validators.ValidationError(self.message)


# Inherit from FlaskForm to get access to form.hidden_tag() and other features
class RegistrationForm(FlaskForm):
    email = EmailField(
        'Email Address',
        validators=[
            validators.DataRequired(),
            validators.Email(),
            EmailValidator()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            validators.DataRequired(),
            validators.Regexp('^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).*$',
                              message='Password should include number, uppercase letter, lowercase letter and special character.')
            ]
    )
    confirm = PasswordField(
        'Confirm Password',
        validators=[
            validators.DataRequired(),
            validators.EqualTo('password', message='Passwords must match.')
        ]
    )
    first_name = StringField(
        'First Name',
        validators=[
            validators.DataRequired()
        ]
    )
    last_name = StringField(
        'Last Name',
        validators=[
            validators.DataRequired()
        ]
    )
    
    
    adulthood_statement = BooleanField(
        Markup('I am over 18 years old and accept <a href="/terms_and_conditions">T&C</a>.'),
        validators=[
            validators.DataRequired()
        ]
    )

    # The system should validate that the email address is not already in use
    def validate_email(self, field):
        if email_exists(field.data):
            raise validators.ValidationError('The email address is already in use.')
