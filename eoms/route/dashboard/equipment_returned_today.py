from eoms import app
from flask import render_template, request, session, jsonify, abort
from datetime import datetime
from eoms.model.db import get_cursor
from eoms.model.booking import get_booking_by_return_date, get_bookingItemList_by_hireto, \
    get_booking_by_return_date_and_store
from eoms.model.booking import confirm_return, get_bookingItemList_by_id, record_return, record_check_out
from eoms.model.session_utils import allow_role, logged_in
from eoms.model.machine import get_machine_by_booking_item_ID


@app.route('/equipment_returned_today', methods=['GET', 'POST'])
def equipment_returned_today():
    if not logged_in():
        abort(401)  # User not logged in, return 401 error

    role = session.get('role')
    user_id = session.get('user_id')
    store_id = session.get('store_id', None)  # If the role is staff or lmgr, there should be store_id in the session

    bookingItemList = []
    if request.method == 'POST':
        date = request.form.get('date')
    else:
        date = datetime.now().strftime('%Y-%m-%d')

    if role in ['staff', 'lmgr']:
        if not store_id:
            abort(403)  # If the role should have a store_id but does not, a 403 error is returned
        # For staff and lmgr, query only the data for the specified shop
        bookings = get_booking_by_return_date_and_store(date, store_id)
    elif role in ['nmgr', 'admin']:
        # For nmgr and admin, query all shop data
        bookings = get_booking_by_return_date(date)
    else:
        abort(403)  # Returns a 403 error if the role is not legal

    booking_id_list = list(set(booking['booking_id'] for booking in bookings))
    unique_bookings = unique_bookings_by_id(bookings)
    bookingItemList = get_bookingItemList_by_hireto(booking_id_list, date)

    return render_template('dashboard/equipment_returned_today.html', bookings= unique_bookings, bookingItemList=bookingItemList, date=date)

# This is the API endpoint for the FullCalendar
@app.route('/api/equipment-returns', methods=['GET'])
def get_equipment_returns():
    if not logged_in():
        return jsonify({'error': 'Unauthorized'}), 401

    role = session.get('role')
    store_id = session.get('store_id', None)

    date_from = request.args.get('start', default=datetime.now().strftime('%Y-%m-%d'))
    date_to = request.args.get('end', default=datetime.now().strftime('%Y-%m-%d'))

    if role in ['staff', 'lmgr']:
        if not store_id:
            return jsonify({'error': 'Forbidden'}), 403
        sql = """
            SELECT bi.hire_to AS end, bi.hire_from AS start, m.sn, p.name, c.first_name, c.last_name, 
                   c.phone, s.store_name, s.address_line1, s.city, u.email
            FROM booking_item bi
            JOIN machine m ON bi.machine_id = m.machine_id
            JOIN product p ON m.product_code = p.product_code
            JOIN booking b ON bi.booking_id = b.booking_id
            JOIN customer c ON b.customer_id = c.customer_id
            JOIN store s ON b.store_id = s.store_id
            JOIN user u ON c.user_id = u.user_id
            WHERE bi.hire_to BETWEEN %s AND %s AND s.store_id = %s
        """
        cursor = get_cursor()
        cursor.execute(sql, (date_from, date_to, store_id))
    elif role in ['nmgr', 'admin']:
        sql = """
            SELECT bi.hire_to AS end, bi.hire_from AS start, m.sn, p.name, c.first_name, c.last_name, 
                   c.phone, s.store_name, s.address_line1, s.city, u.email
            FROM booking_item bi
            JOIN machine m ON bi.machine_id = m.machine_id
            JOIN product p ON m.product_code = p.product_code
            JOIN booking b ON bi.booking_id = b.booking_id
            JOIN customer c ON b.customer_id = c.customer_id
            JOIN store s ON b.store_id = s.store_id
            JOIN user u ON c.user_id = u.user_id
            WHERE bi.hire_to BETWEEN %s AND %s
        """
        cursor = get_cursor()
        cursor.execute(sql, (date_from, date_to))
    else:
        return jsonify({'error': 'Forbidden'}), 403

    events = cursor.fetchall()

    # Format events for FullCalendar
    results = [{
        'title': f"{event['name']} (SN: {event['sn']})",
        'start': event['start'].strftime('%Y-%m-%dT%H:%M:%S'),
        'end': event['end'].strftime('%Y-%m-%dT%H:%M:%S'),
        'allDay': True,
        'customerName': f"{event['first_name']} {event['last_name']}",
        'customerPhone': event['phone'],
        'storeName': event['store_name'],
        'storeAddress': f"{event['address_line1']}, {event['city']}",
        'customerEmail': event['email']
    } for event in events]

    return jsonify(results)

@app.route('/calendar', methods=['GET', 'POST'])
def get_equipment_returns_calendar():
    return render_template('dashboard/fullcalendar.html')



@app.route('/equipment_return', methods=['GET', 'POST'])
def equipment_return():
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    user_id = session['user_id']

    if request.method == 'POST':
        booking_item_id = request.form.get('id')
        machine = get_machine_by_booking_item_ID(booking_item_id)
        confirm_return(machine['machine_id'])
        record_return(booking_item_id,user_id)
        return jsonify({'status': 'success', 'message': 'Checkout confirmed'})

def unique_bookings_by_id(bookings):
    seen_ids = set()
    unique_bookings = []
    for booking in bookings:
        if booking['booking_id'] not in seen_ids:
            seen_ids.add(booking['booking_id'])
            unique_bookings.append(booking)
    return unique_bookings