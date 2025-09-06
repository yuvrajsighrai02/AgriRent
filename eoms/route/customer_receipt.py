from eoms import app
from flask import render_template, abort
from eoms.model import db
from eoms.model.session_utils import allow_role

@app.route('/receipt/<int:booking_id>')
@allow_role(['customer'])
def receipt(booking_id):
    """Displays the final receipt page for a given booking."""
    booking_detail = get_booking_detail_by_id(booking_id)
    booking_item_list = get_booking_item_list(booking_id)

    if not booking_detail:
        # If the booking ID is invalid or doesn't belong to the user, show a 404 error.
        abort(404, description="Booking not found.")

    # Calculate GST from the total amount
    total = booking_detail.get('total', 0)
    gst = round(total * 3 / 23, 2)

    return render_template('customer/receipt.html',
                           booking_detail=booking_detail,
                           booking_item_list=booking_item_list,
                           gst=gst)

def get_booking_detail_by_id(booking_id):
    """
    Fetches all necessary details for the receipt header from the
    booking, customer, and store tables.
    """
    try:
        # This query now fetches all the necessary details, using 'create_date' directly.
        sql = """
            SELECT
                b.booking_id, b.create_date, b.total, b.note, b.status,
                c.first_name, c.last_name, c.phone, c.address_line1, c.city, u.email,
                s.store_name, s.phone AS store_phone, s.email AS store_email,
                s.address_line1 AS store_address
            FROM booking b
            JOIN customer c ON b.customer_id = c.customer_id
            JOIN user u ON c.user_id = u.user_id
            JOIN store s ON b.store_id = s.store_id
            WHERE b.booking_id = %s;
        """
        cursor = db.get_cursor()
        cursor.execute(sql, (booking_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching booking detail for receipt: {e}")
        return None

def get_booking_item_list(booking_id):
    """
    Fetches all line items associated with a specific booking for the receipt.
    """
    try:
        # This query calculates the number of hire days and the subtotal for each item.
        sql = """
            SELECT
                bi.hire_from, bi.hire_to, bi.hire_rate,
                p.name, p.product_code, m.sn,
                DATEDIFF(bi.hire_to, bi.hire_from) AS hire_days,
                (DATEDIFF(bi.hire_to, bi.hire_from) * bi.hire_rate) AS subtotal
            FROM booking_item bi
            JOIN machine m ON bi.machine_id = m.machine_id
            JOIN product p ON m.product_code = p.product_code
            WHERE bi.booking_id = %s;
        """
        cursor = db.get_cursor()
        cursor.execute(sql, (booking_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching booking items for receipt: {e}")
        return []
