from wtforms import Form, BooleanField, StringField, SelectField, validators, EmailField, TextAreaField
from eoms.model import store
import re

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


class ContactForm(Form):
    email = EmailField(
        'Email Address',
        validators=[
            validators.DataRequired(),
            validators.Email(),
            EmailValidator()
        ]
    )
    store = SelectField(
        'Select store',
        validators=[
            validators.DataRequired()
        ]
    )
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
    enquiry_type = SelectField(
        'Equiry type',
        choices=[
            ('General enquiry', 'General enquiry'),
            ('Account enquiry', 'Account enquiry'),
            ('Booking enquiry', 'Booking enquiry'),
            ('Product equiry', 'Product equiry'),
            ('Other', 'Other')
        ],
        validators=[
            validators.DataRequired()
        ]
    )
    enquiry = TextAreaField(
        'Equiry',
        validators=[
            validators.DataRequired()
        ]
    )
    
    def __init__(self, *args, **kwargs):
        # Render store list
        super(ContactForm, self).__init__(*args, **kwargs)
        self.store.choices = self.get_store_choices()
    
    @staticmethod
    def get_store_choices():
        store_list = store.get_all_active_stores()
        return [(store['store_id'], store['store_name']) for store in store_list]  

