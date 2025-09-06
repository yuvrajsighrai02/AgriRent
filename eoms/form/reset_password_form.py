# Import FlaskForm instead of the basic Form
from flask_wtf import FlaskForm
from wtforms import PasswordField, validators, EmailField
from eoms.form.registration_form import EmailValidator

# Inherit from FlaskForm
class ResetPasswordForm(FlaskForm):
    email = EmailField(
        'Email Address',
        validators=[
            validators.DataRequired(),
            validators.Email(),
            EmailValidator()
        ]
    )

# Inherit from FlaskForm
class ResetPasswordConfirmForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[
            validators.DataRequired(),
            validators.Regexp('^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).*$',
                              message='Password should include number, uppercase letter, lowercase letter and special character.')
            ]
    )
    # Renamed this field to match the template ('confirm' -> 'confirm_password')
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            validators.DataRequired(),
            validators.EqualTo('password', message='Passwords must match.')
        ]
    )
