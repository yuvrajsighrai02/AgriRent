from wtforms import Form, BooleanField, StringField, DateField, PasswordField, SelectField, validators, EmailField, TextAreaField
from wtforms.validators import ValidationError
import re
from markupsafe import Markup

class BookingForm(Form):
    first_name = StringField(
        'First name',
        validators=[
            validators.DataRequired()
        ]
    )
    last_name = StringField(
        'Last name',
        validators=[
            validators.DataRequired()
        ]
    )
    email = EmailField(
        'Email Address',
        validators=[
            validators.DataRequired(),
            validators.Email()
        ]
    )
    phone = StringField(
        'Phone number',
        validators=[
            validators.DataRequired()
        ]
    )
    address_line_1 = StringField(
        'Address line 1',
        validators=[
            validators.DataRequired()
        ]
    )
    # address_line_2 = StringField(
    #     'Address line 2',
    #     validators=[

    #     ]
    # )
    # suburb = StringField(
    #     'Suburb',
    #     validators=[

    #     ]
    # )
    city = StringField(
        'City/Town',
        validators=[

        ]
    )
    # post_code = StringField(
    #     'Post code',
    #     validators=[

    #     ]
    # )
    note = TextAreaField(
        'Note to store',
        validators=[

        ]
    )
    card_number = StringField(
        'Card number',
        validators=[
            validators.DataRequired()
        ]
    )
    card_name = StringField(
        'Name on card',
        validators=[
            validators.DataRequired()
        ]
    )
    card_expiry = StringField(
        'Expire date',
        validators=[
            validators.DataRequired()
        ]
    )
    card_cvv = StringField(
        'CVV',
        validators=[
            validators.DataRequired()
        ]
    )
    accept_tnc = BooleanField(
        Markup('I am over 18 years old and accept <a href="/terms_and_conditions")}}">T&C</a>.'),
        validators=[
            validators.DataRequired()
        ]
    )

# Validate phone number format
# 8 to 12 digits long starting with 0
def validate_phone_number(form, field):
    phone_number = field.data
    if not re.match(r'^0\d{7,11}$', phone_number):
        raise ValidationError('Phone number must start with 0 and be between 8 and 12 digits long.')
