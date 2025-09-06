from flask_wtf import FlaskForm
from wtforms import TextAreaField, RadioField, SubmitField
from wtforms.validators import DataRequired, Length

class TestimonialForm(FlaskForm):
    """
    Form for customers to submit testimonials.
    """
    rating = RadioField(
        'Your Rating',
        choices=[
            ('5', '★★★★★'),
            ('4', '★★★★☆'),
            ('3', '★★★☆☆'),
            ('2', '★★☆☆☆'),
            ('1', '★☆☆☆☆')
        ],
        validators=[DataRequired(message="Please select a rating.")]
    )
    
    testimonial_text = TextAreaField(
        'Your Feedback',
        validators=[
            DataRequired(message="Please share your experience."),
            Length(min=20, max=500, message="Feedback must be between 20 and 500 characters.")
        ],
        render_kw={"placeholder": "Tell us about your experience with our service..."}
    )
    
    submit = SubmitField('Submit Testimonial')
