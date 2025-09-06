import time
import secrets
from eoms.model.db import get_cursor
# Module to handle token generation and validation


# Function to generate a token with an expiry time
def generate_token(email, expiry_minutes=30):
    cursor = get_cursor()
    # Generate a random token
    token = secrets.token_hex(16)  
    # Set expire time 
    expiry_time = time.time() + (expiry_minutes * 60) 
    query = 'INSERT INTO reset_tokens (token, email, expiry_time) VALUES (%(token)s, %(email)s, %(expiry_time)s);'
    values = {'token': token, 'email': email, 'expiry_time': expiry_time}
    cursor.execute(query, values)
    return token

# Function to check if a token is valid
def is_token_valid(token):
    reset_token = get_reset_token_by_token(token)
    if reset_token:
        # Check if the token has expired
        if time.time() <= reset_token['expiry_time']:
            return reset_token['email']
        else:
            # Remove expired token
            delete_reset_token_by_token(token)
    return False

# Get resettoken row by token
def get_reset_token_by_token(token):
    cursor = get_cursor()
    query = 'SELECT * FROM reset_tokens WHERE token = %(token)s;'
    cursor.execute(query, {'token': token})
    return cursor.fetchone()

# Delete resettoken row by token
def delete_reset_token_by_token(token):
    cursor = get_cursor()
    delete_query = 'DELETE FROM reset_tokens WHERE token = %(token)s'
    cursor.execute(delete_query, {'token': token})
    return cursor.rowcount