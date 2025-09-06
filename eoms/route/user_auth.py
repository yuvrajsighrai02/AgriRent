import bcrypt
from eoms import app
from flask import render_template, redirect, request, flash, url_for, session, jsonify
from eoms.form.login_form import LoginForm
from eoms.form.registration_form import RegistrationForm
from eoms.form.reset_password_form import ResetPasswordForm, ResetPasswordConfirmForm
from eoms.model import auth, customer, staff, cart, cart_utils, mail, token_utils
from eoms.model.session_utils import allow_role, logged_in
from eoms.const import STAFF_ROLE_LIST

# ==============================================================================
# ROUTE FOR MODAL LOGIN (UPDATED)
# ==============================================================================
@app.route('/ajax_login', methods=['POST'])
def ajax_login():
    """
    Handles login requests from the modal.
    Responds with JSON and adds profile picture to session on success.
    """
    form = LoginForm(request.form)
    if form.validate():
        role = auth.login_by_email(form.email.data, form.password.data)
        if role:
            redirect_url = url_for('home') 
            
            user_profile = None
            if role == 'customer':
                user_profile = customer.get_customer_by_user_id(session["user_id"])
                if user_profile:
                    session["customer_id"] = user_profile['customer_id']
                    cart_utils.merge_customer_cart(session["customer_id"])
            elif role in STAFF_ROLE_LIST:
                user_profile = staff.get_staff_by_user_id(session["user_id"])
                redirect_url = url_for('dashboard')
            
            if user_profile and user_profile.get('profile_picture'):
                session['profile_picture'] = user_profile['profile_picture']
            else:
                session['profile_picture'] = 'default.png'
            
            return jsonify({'success': True, 'redirect': redirect_url})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password.'})
    else:
        return jsonify({'success': False, 'message': 'Invalid form data. Please check your input.'})


# --- The rest of your user_auth.py file remains the same ---
# Routes for user registration, login, and logout
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        # --- THIS IS THE FIX ---
        # The add_user function now handles the transaction and returns both IDs.
        user_id, customer_id = auth.add_user(
            form.email.data, 
            form.password.data, 
            form.first_name.data, 
            form.last_name.data
        )
        
        if user_id and customer_id:
            # Create a shopping cart for the new customer
            cart.add_cart(customer_id)
            flash('Thanks for registering! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. This email may already be in use.', 'danger')
            return render_template('/auth/register.html', form=form, form_errors=form.errors)
    return render_template('/auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    form_error = None
    if request.method == 'POST' and form.validate():
        role = auth.login_by_email(form.email.data, form.password.data)
        if role:
            if role in STAFF_ROLE_LIST:
                return redirect(url_for('dashboard'))
            elif session["role"] == 'customer':
                user = customer.get_customer_by_user_id(session["user_id"])
                if user:
                    session["customer_id"] = user['customer_id']
                
                previous_page = form.previous_url.data
                cart_utils.merge_customer_cart(session.get("customer_id"))
                
                hire_notification_list = auth.booking_hire_notification(session.get("customer_id"))
                if hire_notification_list:
                    for row in hire_notification_list:
                        flash(f"Notification: Machine SN: {row['sn']},  Hire Date: {row['hire_from'].strftime('%d/%m/%Y %H:%M:%S')}", 'danger')
                return_notification_list = auth.booking_return_notification(session.get("customer_id"))
                if return_notification_list:
                    for row in return_notification_list:
                        flash(f"Notification: Machine SN: {row['sn']},  Return Date: {row['hire_to'].strftime('%d/%m/%Y %H:%M:%S')}", 'danger')
     
                if previous_page:
                    return redirect(previous_page)
                else:
                    return redirect(url_for('home'))
        else:
            form_error = "Invalid email or password. Please try again."
            return render_template("/auth/login.html", form=form, form_error=form_error, form_errors=form.errors)
    else:
        return render_template("/auth/login.html", form=form)

# Clear session and logout user, return to home page
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        if auth.email_exists(email):
            token = token_utils.generate_token(email)
            body = f'Click the following link to reset your password: {url_for("reset_password_confirm", token=token, _external=True)}'
            
            mail.send_email(
                from_email=app.config.get('MAIL_USERNAME'), 
                to_email=email, 
                subject='Password Reset Request', 
                body=body
            )
        
        flash('If an account with that email exists, a password reset link has been sent.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/reset_password.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_confirm(token):
    email = token_utils.is_token_valid(token)
    if email:
        form = ResetPasswordConfirmForm(request.form)
        if request.method == 'POST' and form.validate():
            hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
            auth.update_password(email, hashed_password)
            token_utils.delete_reset_token_by_token(token)
            flash('Password has been updated.', 'success')
            return redirect(url_for('login'))
        return render_template('auth/reset_password_confirm.html', form=form, token=token)
    else:
        flash('Token is invalid or expired. Please request a new one.', 'danger')
        return redirect(url_for('reset_password'))
