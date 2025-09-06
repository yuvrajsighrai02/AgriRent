from wtforms import Form, PasswordField, validators, EmailField, HiddenField
from eoms.form.registration_form import EmailValidator

class LoginForm(Form):
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
    previous_url = HiddenField('Previous URL')
