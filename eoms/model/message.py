from eoms.model import db
from flask import jsonify

def get_threads_for_customer(customer_id):
    cursor = db.get_cursor()
    sql = """
        SELECT t.thread_id, t.subject, t.last_updated, t.customer_unread, s.store_name
        FROM message_threads t
        JOIN store s ON t.store_id = s.store_id
        WHERE t.customer_id = %s
        ORDER BY t.last_updated DESC
    """
    cursor.execute(sql, (customer_id,))
    return cursor.fetchall()

def get_threads_for_store(store_id):
    cursor = db.get_cursor()
    sql = """
        SELECT t.thread_id, t.subject, t.last_updated, t.staff_unread, c.first_name, c.last_name
        FROM message_threads t
        JOIN customer c ON t.customer_id = c.customer_id
        WHERE t.store_id = %s
        ORDER BY t.last_updated DESC
    """
    cursor.execute(sql, (store_id,))
    return cursor.fetchall()

def get_messages_in_thread(thread_id, user_id):
    cursor = db.get_cursor()
    sql = """
        SELECT m.message_text, m.created_at, u.role, u.user_id,
               c.first_name AS customer_first_name, s.first_name AS staff_first_name
        FROM messages m
        JOIN user u ON m.user_id = u.user_id
        LEFT JOIN customer c ON u.user_id = c.user_id
        LEFT JOIN staff s ON u.user_id = s.user_id
        WHERE m.thread_id = %s
        ORDER BY m.created_at ASC
    """
    cursor.execute(sql, (thread_id,))
    messages = cursor.fetchall()
    
    # Mark messages as read
    user_role_sql = "SELECT role FROM user WHERE user_id = %s"
    cursor.execute(user_role_sql, (user_id,))
    role = cursor.fetchone()['role']
    
    if role == 'customer':
        update_sql = "UPDATE message_threads SET customer_unread = FALSE WHERE thread_id = %s"
    else:
        update_sql = "UPDATE message_threads SET staff_unread = FALSE WHERE thread_id = %s"
    cursor.execute(update_sql, (thread_id,))
    db.connection.commit()
    
    return messages

def create_new_thread(customer_id, store_id, subject, initial_message, user_id):
    cursor = db.get_cursor()
    try:
        cursor.execute("START TRANSACTION;")
        # Create the thread
        thread_sql = """
            INSERT INTO message_threads (customer_id, store_id, subject)
            VALUES (%s, %s, %s)
        """
        cursor.execute(thread_sql, (customer_id, store_id, subject))
        thread_id = cursor.lastrowid

        # Add the first message
        message_sql = """
            INSERT INTO messages (thread_id, user_id, message_text)
            VALUES (%s, %s, %s)
        """
        cursor.execute(message_sql, (thread_id, user_id, initial_message))
        
        db.connection.commit()
        return thread_id
    except Exception as e:
        db.connection.rollback()
        print(f"Error creating new thread: {e}")
        return None

def add_reply_to_thread(thread_id, user_id, message_text):
    cursor = db.get_cursor()
    try:
        cursor.execute("START TRANSACTION;")
        # Add the new message
        message_sql = """
            INSERT INTO messages (thread_id, user_id, message_text)
            VALUES (%s, %s, %s)
        """
        cursor.execute(message_sql, (thread_id, user_id, message_text))
        
        # Mark the thread as unread for the other party
        user_role_sql = "SELECT role FROM user WHERE user_id = %s"
        cursor.execute(user_role_sql, (user_id,))
        role = cursor.fetchone()['role']
        
        if role == 'customer':
            update_sql = "UPDATE message_threads SET staff_unread = TRUE, customer_unread = FALSE WHERE thread_id = %s"
        else:
            update_sql = "UPDATE message_threads SET customer_unread = TRUE, staff_unread = FALSE WHERE thread_id = %s"
        cursor.execute(update_sql, (thread_id,))
        
        db.connection.commit()
        return True
    except Exception as e:
        db.connection.rollback()
        print(f"Error adding reply: {e}")
        return False
