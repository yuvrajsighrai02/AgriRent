from flask import jsonify
from eoms import app
from eoms.model.db import get_cursor


# Display customer information in Check Out Today
@app.route('/get_customer_details/<int:customer_id>')
def get_customer_details(customer_id):
    try:
        cursor = get_cursor()
        query = """
        SELECT c.first_name, c.last_name, c.phone, c.address_line1, c.city, s.store_name, u.email
        FROM customer c
        JOIN store s ON c.my_store = s.store_id
        JOIN user u ON c.user_id = u.user_id
        WHERE c.customer_id = %s
        """
        cursor.execute(query, (customer_id,))
        customer_details = cursor.fetchone()
        return jsonify(customer_details)
    except Exception as e:
        print("Error fetching customer details:", e)
        return jsonify({'error': 'Unable to fetch customer details'}), 500


# Display customer information in Equipment returned today
@app.route('/get_customer_details_returned/<int:customer_id>')
def get_customer_details_returned(customer_id):
    try:
        cursor = get_cursor()
        query = """
        SELECT c.first_name, c.last_name, c.phone, c.address_line1, c.city, s.store_name, u.email
        FROM customer c
        JOIN store s ON c.my_store = s.store_id
        JOIN user u ON c.user_id = u.user_id
        WHERE c.customer_id = %s
        """
        cursor.execute(query, (customer_id,))
        customer_details = cursor.fetchone()
        return jsonify(customer_details)
    except Exception as e:
        print("Error fetching customer details:", e)
        return jsonify({'error': 'Unable to fetch customer details'}), 500
