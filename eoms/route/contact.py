from eoms import app
from flask import render_template, redirect, request, flash, url_for
from eoms.form.contact_form import ContactForm
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import requests
from eoms.model import mail, message
from eoms.secret import RECAPTCHA_SECRET_KEY

# Route for Contact us page

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)
    if request.method == 'POST':
        # Validate reCAPTCHA
        recaptcha_response = request.form['g-recaptcha-response']
        secret_key = RECAPTCHA_SECRET_KEY
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', 
                                 data={'secret': secret_key, 'response': recaptcha_response})
        result = response.json()
        if not result['success']:
            flash('reCAPTCHA validation failed. Please try again.')
            return redirect(url_for('contact'))
        # Process form sbumission
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        store_id = form.store.data
        enquiry_type = form.enquiry_type.data
        enquiry = form.enquiry.data
        # Send message to store
        subject = f"Contact Form Submission from {first_name} {last_name}"
        body = f"Name: {first_name} {last_name}\nEmail: {email}\nEquiry type: {enquiry_type}\n\nEnquiry:\n{enquiry}"
        # response = mail.send_email(from_email=email, to_email='agrihire.aq@gmail.com', subject=subject, body=body)
        time = datetime.now()
        # Sending to store message system
        response = message.add_new_message_BycustomerID(6,subject,body,time, store_id)
        if response.json['success']:
            flash('Message sent successfully!', 'success')
        else:
            flash(f'An error occurred: {response.json["message"]}', 'danger')
        # return redirect(url_for('contact'))
    return render_template('/shopping/contact.html', form=form)

