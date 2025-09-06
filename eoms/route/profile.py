import os
import uuid
from werkzeug.utils import secure_filename
from eoms import app
from flask import render_template, redirect, request, flash, url_for, session
from eoms.model import db
from eoms.model.session_utils import allow_role
import bcrypt

# Configuration for file uploads
UPLOAD_FOLDER = 'eoms/static/images/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# View and update profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    allow_role(['customer', 'staff', 'lmgr', 'nmgr', 'admin'])
    user_id = session['user_id']
    role = session['role']

    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                # Create a secure, unique filename
                filename = secure_filename(file.filename)
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                
                # Update the database with the new filename
                cursor = db.get_cursor()
                if role == 'customer':
                    sql = 'UPDATE customer SET profile_picture = %s WHERE user_id = %s'
                else:
                    sql = 'UPDATE staff SET profile_picture = %s WHERE user_id = %s'
                cursor.execute(sql, (unique_filename, user_id))
                db.connection.commit()
                
                # Update the session with the new picture
                session['profile_picture'] = unique_filename
                flash('Profile picture updated successfully!', 'success')
                return redirect(url_for('profile'))

        # Handle text field updates
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        cursor = db.get_cursor()
        if role == 'customer':
            address_line1 = request.form.get('address1')
            city = request.form.get('city')
            sql = '''UPDATE customer 
                     SET first_name=%s, last_name=%s, phone=%s, address_line1=%s, city=%s
                     WHERE user_id=%s;'''
            cursor.execute(sql, (first_name, last_name, phone, address_line1, city, user_id))
        else:
            position = request.form.get('position')
            sql = 'UPDATE staff SET first_name=%s, last_name=%s, position=%s, phone=%s WHERE user_id=%s;'
            cursor.execute(sql, (first_name, last_name, position, phone, user_id))
        
        db.connection.commit()
        flash('Profile details updated successfully!', 'success')
        return redirect(url_for('profile'))

    # For GET request, fetch and display profile
    cursor = db.get_cursor()
    if role == 'customer':
        sql = 'SELECT * FROM customer WHERE user_id=%s;'
    else:
        sql = 'SELECT * FROM staff WHERE user_id=%s;'
    cursor.execute(sql, (user_id,))
    profile_data = cursor.fetchone()
    return render_template('profile/profile.html', profile=profile_data)
        
# ... (Your change_password function remains the same)
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    msg = ''  
    allow_role(['customer', 'staff', 'lmgr', 'nmgr', 'admin'])
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Check if the current password is correct
        cursor = db.get_cursor()
        cursor.execute('SELECT password FROM user WHERE user_id = %s', (session.get('user_id'),))
        row = cursor.fetchone()
        if row:
            user_bytes = current_password.encode('utf-8')
            user_password = row['password'].encode('utf-8')
            if bcrypt.checkpw(user_bytes, user_password):
                # Check if the new password and confirm password match
                if new_password == confirm_password:
                    # Check if the new password is different from the current password
                    if new_password != current_password:
                        # Update the password
                        bytes = new_password.encode('utf-8') 
                        salt = bcrypt.gensalt() 
                        hashed_password = bcrypt.hashpw(bytes, salt) 
                        cursor.execute('UPDATE user SET password=%s WHERE user_id = %s', (hashed_password, session.get('user_id')))
                        db.connection.commit()
                        flash('Password updated successfully!', 'success')
                    else:
                        msg = 'New password must be different from the current password.'
                else:
                    msg = 'New password and confirmation password do not match.'
            else:
                msg = 'Incorrect current password.'
    return render_template('profile/change_password.html', msg = msg)
