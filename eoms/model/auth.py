from eoms.model.db import get_cursor, get_connection
import bcrypt
from flask import session
from mysql.connector import Error

# This module handles user authentication, i.e. login
# and any function in realation to password hashinng, i.e. register, change password

# Check if email exists in db
def email_exists(email):
    query = """SELECT *
            FROM user
            WHERE email = %(email)s;
            """
    connection = get_cursor()
    connection.execute(query, {"email": email})
    user = connection.fetchone()
    return True if user else False

def login_by_email(email, password):
    # Query username in db user table
    query = """SELECT * FROM user 
            WHERE email = %(email)s;
            """
    connection = get_cursor()
    connection.execute(query, {"email": email})
    user = connection.fetchone()
    # If user exists and is active
    if user and user.get('is_active'):
        # Check if password matches
        user_bytes = password.encode('utf-8')
        user_password = user['password'].encode('utf-8')
        if bcrypt.checkpw(user_bytes, user_password):
            session['loggedin'] = True
            session["user_id"] = user["user_id"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            if user["role"] == 'customer':
                customer_query = "SELECT customer_id FROM customer WHERE user_id = %(user_id)s"
                connection.execute(customer_query, {'user_id': user['user_id']})
                customer_data = connection.fetchone()
                if customer_data:
                    session['customer_id'] = customer_data['customer_id']
                else:
                    print(f"Warning: User {user['user_id']} has role 'customer' but no matching customer record found.")
            
            return user["role"]
    else:
        return None

# Add a user to db, default role is customer
def add_user(email, password, first_name, last_name, role='customer'):
    """
    Creates a new user and a corresponding customer record within a single,
    safe database transaction.
    Returns a tuple of (user_id, customer_id) on success, otherwise None.
    """
    try:
        with get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                # Hash the password
                bytes = password.encode('utf-8')
                salt = bcrypt.gensalt()
                hash_pw = bcrypt.hashpw(bytes, salt)

                # Insert into user table
                user_query = """INSERT INTO user (`email`, `password`, `role`) 
                                VALUES (%(email)s, %(password)s, %(role)s);"""
                cursor.execute(user_query, {'email': email, 'password': hash_pw, 'role': role})
                
                if cursor.rowcount != 1:
                    raise Exception("Failed to create user record.")
                
                user_id = cursor.lastrowid

                # --- THIS IS THE FIX ---
                # Set a default store for the new customer. We'll use store_id = 1.
                default_store_id = 1

                # Insert into customer table
                customer_query = """INSERT INTO customer (`user_id`, `first_name`, `last_name`, `my_store`) 
                                    VALUES (%(user_id)s, %(first_name)s, %(last_name)s, %(my_store)s);"""
                cursor.execute(customer_query, {
                    'user_id': user_id, 
                    'first_name': first_name, 
                    'last_name': last_name,
                    'my_store': default_store_id
                })

                if cursor.rowcount != 1:
                    raise Exception("Failed to create customer record.")

                customer_id = cursor.lastrowid
                
                # Commit the transaction to save both records
                connection.commit()
                
                return user_id, customer_id

    except Error as e:
        print(f"Database error during user registration: {e}")
        return None, None


# For the reset password feature
def update_password(email, hashed_password):
    # This function also needs a commit to save the change
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                query = """UPDATE user SET password = %s WHERE email = %s"""
                cursor.execute(query, (hashed_password, email))
                connection.commit()
    except Error as e:
        print(f"Error updating password: {e}")


#Notification for booking hire
def booking_hire_notification(customer_id):
    sql = '''SELECT m.sn, bi.hire_from
            FROM `booking` b
            INNER JOIN booking_item bi ON b.booking_id = bi.booking_id
            INNER JOIN machine m ON m.machine_id = bi.machine_id
            WHERE b.customer_id = %s
            AND bi.hire_from BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 3 DAY)
            ORDER BY bi.hire_from;'''    
    cursor = get_cursor()   
    cursor.execute(sql, (customer_id,))
    return cursor.fetchall()

#Notification for booking return    
def booking_return_notification(customer_id):
    sql = '''SELECT m.sn,bi.hire_to
                FROM `booking` b
                INNER JOIN booking_item bi ON b.booking_id = bi.booking_id
                INNER JOIN machine m ON m.machine_id = bi.machine_id
                WHERE b.customer_id = %s
                AND bi.hire_to BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 3 DAY)
                ORDER BY bi.hire_to; '''
    
    cursor = get_cursor()   
    cursor.execute(sql, (customer_id,)) 
    return cursor.fetchall()
