from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, DateField, DateTimeLocalField, SelectField, validators, HiddenField, TextAreaField, IntegerField
from datetime import datetime, timedelta
from eoms.model import store

class CustomDateTimeLocalField(DateTimeLocalField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%dT%H:%M', **kwargs):
        super().__init__(label, validators, format=format, **kwargs)
        self.widget.step = 1800  # 30 minutes in seconds

class ProductShoppingForm(Form):
    store = SelectField(
        'Select store',
        validators=[
            validators.DataRequired()
        ]
    )
    # qty = IntegerField(
    #     'Quantity', 
    #     validators=[
    #         validators.DataRequired(), 
    #         validators.NumberRange(min=1, message="Quantity must be at least 1")
    #     ]
    # )
    hire_from = DateTimeLocalField(
        'Hire from',
        format='%Y-%m-%dT%H:%M',
        validators=[
            validators.DataRequired()
        ]
    )
    hire_to = DateTimeLocalField(
        'Hire to',
        format='%Y-%m-%dT%H:%M',
        validators=[
            validators.DataRequired()
        ]
    )
    product_code = HiddenField('Product code')
    min_hire = HiddenField('Min Hire')
    max_hire = HiddenField('Max Hire')


    def __init__(self, *args, **kwargs):
        # Render store list
        super(ProductShoppingForm, self).__init__(*args, **kwargs)
        self.store.choices = self.get_store_choices()
        # Set hire from and hire to min value based on current time
        now = datetime.now()
        if now.hour < 6:
            min_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
        elif now.hour >= 17:
            min_time = (now + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
        else:
            minutes = (now.minute // 30 + 1) * 30
            if minutes == 60:
                min_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
            else:
                min_time = now.replace(minute=minutes, second=0, microsecond=0)

        min_time_str = min_time.strftime('%Y-%m-%dT%H:%M')
        self.hire_from.render_kw = {'min': min_time_str}
        self.hire_to.render_kw = {'min': min_time_str}

    @staticmethod
    def get_store_choices():
        store_list = store.get_all_active_stores()
        return [('','Select a store')] + [(store['store_id'], store['store_name']) for store in store_list]

    def validate_hire_from(self, field):
        if field.data < datetime.now():
            raise validators.ValidationError("You cannot select a time in the past")

    def validate_hire_to(self, field):
        if field.data < self.hire_from.data:
            raise validators.ValidationError("You cannot select a return before the start time")
        min_hire_period = timedelta(days=int(self.min_hire.data))
        max_hire_period = timedelta(days=int(self.max_hire.data))
        if field.data - self.hire_from.data < min_hire_period:
            raise validators.ValidationError(f"Hire period must be at least {self.min_hire.data} day(s)")
        if field.data - self.hire_from.data > max_hire_period:
            raise validators.ValidationError(f"Hire period must not exceed {self.max_hire.data} day(s)")