from eoms.model.db import get_cursor
from flask import jsonify, abort

# Module to hanlde queries related to staff table

# Return a staff by user id
def get_staff_by_user_id(user_id):
    connection  = get_cursor()
    query = """
            SELECT * FROM staff
            WHERE user_id = %(user_id)s;
            """
    connection.execute(query, {'user_id': user_id})
    return connection.fetchone()