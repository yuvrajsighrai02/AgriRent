from eoms import app
from flask import render_template
from eoms.model.db import get_cursor
from collections import defaultdict
from flask import session, abort
from eoms.model.session_utils import logged_in, allow_role

# Route to display booking data
@app.route('/dashboard/bookings')
def bookings():
    if not logged_in():
        abort(401)  # User not logged in, return 401 error

    role = session.get('role')
    user_id = session.get('user_id')
    store_id = session.get('store_id', None)  # If the role is staff or lmgr, there should be store_id in the session

    cursor = get_cursor()

    if role in ['staff', 'lmgr']:
        if not store_id:
            abort(403)  # If the role should have a store_id but does not, a 403 error is returned
        # Query only the booking data of the shops associated with the staff or local manager.
        query = '''
            SELECT b.booking_id, b.create_date, c.first_name, c.last_name, c.phone, u.email,
                   bi.machine_id, bi.hire_from, bi.hire_to, bi.hire_rate, 
                   m.sn, p.desc, p.product_code
            FROM booking b
            JOIN customer c ON b.customer_id = c.customer_id
            JOIN user u ON c.user_id = u.user_id
            JOIN booking_item bi ON bi.booking_id = b.booking_id
            JOIN machine m ON bi.machine_id = m.machine_id
            JOIN product p ON m.product_code = p.product_code
            WHERE b.store_id = %s
            ORDER BY c.first_name, c.last_name, b.create_date
        '''
        cursor.execute(query, (store_id,))
    elif role in ['nmgr', 'admin']:
        # Check booking data for all shops
        query = '''
            SELECT b.booking_id, b.create_date, c.first_name, c.last_name, c.phone, u.email,
                   bi.machine_id, bi.hire_from, bi.hire_to, bi.hire_rate, 
                   m.sn, p.desc, p.product_code
            FROM booking b
            JOIN customer c ON b.customer_id = c.customer_id
            JOIN user u ON c.user_id = u.user_id
            JOIN booking_item bi ON bi.booking_id = b.booking_id
            JOIN machine m ON bi.machine_id = m.machine_id
            JOIN product p ON m.product_code = p.product_code
            ORDER BY c.first_name, c.last_name, b.create_date
        '''
        cursor.execute(query)
    else:
        abort(403)  # Returns a 403 error if the role is not staff, lmgr, nmgr, or admin

    raw_bookings = cursor.fetchall()
    bookings = defaultdict(list)
    for booking in raw_bookings:
        customer_key = (booking['first_name'], booking['last_name'], booking['phone'], booking['email'])
        bookings[customer_key].append(booking)

    return render_template('dashboard/bookings.html', bookings=bookings)
