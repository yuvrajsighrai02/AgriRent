from eoms.model.db import get_cursor
from flask import jsonify, abort

# Module to hanlde queries related to customer table

# Return a customer by user id
def get_customer_by_user_id(user_id):
    connection  = get_cursor()
    query = """
            SELECT * FROM customer
            WHERE user_id = %(user_id)s;
            """
    connection.execute(query, {'user_id': user_id})
    return connection.fetchone()

# Return my store of a customer
def get_my_store_by_customer_id(customer_id):
    connection  = get_cursor()
    query = """
            SELECT my_store FROM customer
            WHERE customer_id = %(customer_id)s;
            """
    connection.execute(query, {'customer_id': customer_id})
    return connection.fetchone()

# Update my store of a customer
def update_my_store_by_customer_id(customer_id, store_id):
    connection  = get_cursor()
    query = """
            UPDATE customer SET my_store = %(store_id)s
            WHERE customer_id = %(customer_id)s;
            """
    connection.execute(
        query,
        {
            'customer_id': customer_id,
            'store_id': store_id
        }
    )
    return True if connection.rowcount == 1 else False


