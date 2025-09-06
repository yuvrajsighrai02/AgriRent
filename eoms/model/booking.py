from flask import jsonify
from datetime import datetime
from mysql.connector import Error
# Import the db object to handle transactions and cursor creation
from eoms.model import db 
# Import other necessary models
from eoms.model import cart
from eoms.model.machine import get_available_machines_by_code_store_date_range

def finalize_booking_from_payment(cart_id, customer_id, store_id, note, payment_intent_id):
    """
    This is the new, primary function for creating a booking after a successful payment.
    It handles the entire database operation within a single, safe transaction.
    """
    connection = None
    try:
        with db.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)

            cart_query = """
                SELECT c.*, p.name, p.image,
                (CEIL(DATEDIFF(c.hire_to, c.hire_from)) * c.hire_rate * c.qty) AS original_subtotal,
                ROUND((CEIL(DATEDIFF(c.hire_to, c.hire_from)) * c.hire_rate * c.qty * (c.disc_rate / 100)), 2) as discount,
                ROUND((CEIL(DATEDIFF(c.hire_to, c.hire_from)) * c.hire_rate * c.qty * (1 - c.disc_rate / 100)), 2) as subtotal
                FROM cart_item c
                INNER JOIN product p ON c.product_code = p.product_code
                WHERE cart_id = %s ORDER BY c.line_num;
            """
            cursor.execute(cart_query, (cart_id,))
            cart_items = cursor.fetchall()

            if not cart_items:
                raise ValueError("Cart is empty. Cannot create booking.")
            
            cart_total = round(sum(item['subtotal'] for item in cart_items), 2)

            booking_sql = """
                INSERT INTO booking (customer_id, store_id, create_date, total, note, status, payment_status, stripe_payment_intent_id) 
                VALUES (%s, %s, %s, %s, %s, 1, 'paid', %s)
            """
            cursor.execute(booking_sql, (customer_id, store_id, datetime.now(), cart_total, note, payment_intent_id))
            booking_id = cursor.lastrowid
            if not booking_id:
                raise Exception("Failed to create the main booking record.")

            for item in cart_items:
                available_machines = get_available_machines_by_code_store_date_range(
                    product_code=item['product_code'], store_id=store_id,
                    date_from=item['hire_from'], date_to=item['hire_to']
                )
                
                if len(available_machines) < item['qty']:
                    raise ValueError(f"Stock for {item['name']} became unavailable. The booking has been cancelled.")

                machines_to_book = available_machines[:item['qty']]
                for machine in machines_to_book:
                    booking_item_sql = """
                        INSERT INTO booking_item (booking_id, machine_id, line_num, hire_rate, hire_from, hire_to, status)
                        VALUES (%s, %s, %s, %s, %s, %s, 1)
                    """
                    cursor.execute(booking_item_sql, (
                        booking_id, machine['machine_id'], item['line_num'],
                        item['hire_rate'], item['hire_from'], item['hire_to']
                    ))

            cursor.execute("DELETE FROM cart_item WHERE cart_id = %s", (cart_id,))
            connection.commit()
            
            print(f"SUCCESS: Booking #{booking_id} created and finalized from PaymentIntent {payment_intent_id}.")
            return booking_id

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"CRITICAL ERROR during booking finalization: {e}")
        return None
    
# Get booking list info by today's date
def get_bookingList_by_date(date):
    cursor = db.get_cursor()
    query = '''SELECT DISTINCT
                b.booking_id,
                b.customer_id,
                b.create_date,
                b.total,
                b.note,
                b.status,
                bi.booking_item_id,
                bi.machine_id,
                bi.line_num,
                bi.hire_rate,
                bi.hire_from,
                c.first_name,
                c.last_name,
                DATE(bi.hire_from) AS hire_from,
                DAY(bi.hire_from) AS hire_from_date,
                DATE_FORMAT(bi.hire_from, '%b') AS hire_from_month,
                bi.hire_to
                FROM 
                    booking b
                JOIN 
                    booking_item bi ON b.booking_id = bi.booking_id
                JOIN 
                    customer c ON b.customer_id = c.customer_id
                WHERE 
                    DATE(bi.hire_from) = %(today)s
                AND
                bi.booking_item_id = (
                    SELECT MIN(bi_inner.booking_item_id)
                    FROM booking_item bi_inner
                    WHERE bi_inner.booking_id = b.booking_id
                );'''
    

    cursor.execute(query, {"today": date})
    return cursor.fetchall()

# Get all booking items info by booking ID
def get_bookingItemList_by_id(id,date):
    cursor = db.get_cursor()

    #if id is a array
    if isinstance(id, list):
        booking_items = []

        unique_ids = list(set(id))

        for booking_id in unique_ids:
            query = '''SELECT 
                        b.booking_item_id,
                        b.booking_id,
                        b.machine_id,
                        b.hire_from,
                        b.hire_to,
                        m.status,
                        m.sn,
                        m.product_code,
                        p.category_code,
                        p.name,
                        p.desc
                        FROM booking_item b
                        INNER JOIN machine m ON b.machine_id = m.machine_id
                        INNER JOIN product p ON m.product_code = p.product_code
                    WHERE 
                        booking_id = %(id)s and DATE(hire_from) = %(date)s;'''
            cursor.execute(query, {"id": booking_id, "date": date})
            booking_items.extend(cursor.fetchall())
        return booking_items

    # if id is not array
    else:
        query = '''SELECT 
                        b.booking_item_id,
                        b.booking_id,
                        b.machine_id,
                        b.hire_from,
                        b.hire_to,
                        b.status,
                        m.sn,
                        m.product_code,
                        p.category_code,
                        p.name,
                        p.desc
                        FROM booking_item b
                        INNER JOIN machine m ON b.machine_id = m.machine_id
                        INNER JOIN product p ON m.product_code = p.product_code
                    WHERE
                    booking_id = %(id)s and DATE(hire_from) = %(date)s;'''
        cursor.execute(query, {"id": id, "date": date})
        return cursor.fetchall()

def get_bookingItemList_by_hireto(id,date):
    cursor = db.get_cursor()

    #if id is a array
    if isinstance(id, list):
        booking_items = []

        unique_ids = list(set(id))

        for booking_id in unique_ids:
            query = '''SELECT 
                        b.booking_item_id,
                        b.booking_id,
                        b.machine_id,
                        b.hire_from,
                        b.hire_to,
                        m.status,
                        m.sn,
                        m.product_code,
                        p.category_code,
                        p.name,
                        p.desc
                        FROM booking_item b
                        INNER JOIN machine m ON b.machine_id = m.machine_id
                        INNER JOIN product p ON m.product_code = p.product_code
                    WHERE 
                        booking_id = %(id)s and DATE(hire_to) = %(date)s;'''
            cursor.execute(
                query, 
                {
                    "id": booking_id,
                    "date": date,
                }
            )
            booking_items.extend(cursor.fetchall())
        return booking_items

    # if id is not array
    else:
        query = '''SELECT 
                        b.booking_item_id,
                        b.booking_id,
                        b.machine_id,
                        b.hire_from,
                        b.hire_to,
                        b.status,
                        m.sn,
                        m.product_code,
                        p.category_code,
                        p.name,
                        p.desc
                        FROM booking_item b
                        INNER JOIN machine m ON b.machine_id = m.machine_id
                        INNER JOIN product p ON m.product_code = p.product_code
                    WHERE
                    booking_id = %(id)s and DATE(hire_to) = %(date)s;'''
        cursor.execute(
            query, 
            {
                "id": id,
                "date": date,
            }
        )
        return cursor.fetchall()   
    
# Get all booking info by Customer ID
def get_my_current_booking(id):
    cursor = db.get_cursor()
    query = '''SELECT * FROM 
                    booking
                WHERE 
                    customer_id = %(id)s;'''
    cursor.execute(
        query, 
        {
            "id": id,
        }
    )
    return cursor.fetchall() 

# Get all booking info by Customer ID and not early then today
def get_my_current_booking_notEarlyToday(id):
    today_date = datetime.now().date()
    cursor = db.get_cursor()
    query = '''
            SELECT b.*
            FROM booking b
            WHERE b.booking_id IN (
                SELECT DISTINCT b.booking_id
                FROM booking b
                INNER JOIN booking_item bi ON b.booking_id = bi.booking_id
                WHERE b.customer_id = %(id)s  AND bi.hire_from >  %(date)s
                ORDER BY b.create_date
            );
           '''
    cursor.execute(
        query, 
        {
            "id": id,
            "date": today_date,
        }
    )
    return cursor.fetchall() 

# Cancel booking info by Customer ID and Booking ID
def cancel_booking_byuserIdAndBookingId(cusID,bookingID):
    cursor = db.get_cursor()
    query = '''UPDATE booking SET status = -1 WHERE booking_id = %(booking_id)s and customer_id = %(customer_id)s;'''
    cursor.execute(
        query, 
        {
            "booking_id": bookingID,
            "customer_id": cusID,
        }
    )
    if cursor.rowcount == 1:
        return jsonify({'success': True,})
    else:
        return jsonify({'success': False, 'error': 'Something went wrong'}), 500 

# Extend booking period by Booking items ID
def extend_booking_period(hire_to,booking_item_id):
    cursor = db.get_cursor()
    query = '''UPDATE booking_item SET hire_to = %(hire_to)s WHERE booking_item_id = %(booking_item_id)s ;'''
    cursor.execute(
        query, 
        {
            "hire_to": hire_to,
            "booking_item_id": booking_item_id,
        }
    )
    if cursor.rowcount == 1:
        return jsonify({'success': True,})
    else:
        return jsonify({'success': False, 'error': 'Something went wrong'}), 500 


# Database queries for equipment_returned_today.html
def get_booking_by_return_date(date):
    cursor = db.get_cursor()
    query = """
            SELECT booking.booking_id, booking.customer_id, booking.create_date, booking.total, booking.note, booking.status,
                   customer.first_name, customer.last_name,
                   booking_item.hire_from, booking_item.hire_to,
                   machine.sn,
                   product.name
            FROM booking
            INNER JOIN customer ON booking.customer_id = customer.customer_id
            INNER JOIN booking_item ON booking.booking_id = booking_item.booking_id
            INNER JOIN machine ON booking_item.machine_id = machine.machine_id
            INNER JOIN product ON machine.product_code = product.product_code
            WHERE DATE(booking_item.hire_to) = %(date)s
            """
    cursor.execute(query, {'date': date})
    return cursor.fetchall()

    
def confirm_check_out (machine_id):
    cursor = db.get_cursor()
    query = """UPDATE machine SET status = 2 WHERE machine_id = %(machine_id)s;"""
    cursor.execute(
        query, 
        {
            "machine_id": machine_id,
        }
    )
    if cursor.rowcount == 1:
        return jsonify({'success': True, 'message': 'Success!'})
    else:
        return jsonify({'success': False, 'message': 'Something went wrong'}), 500
    
def record_check_out(booking_item_id,staff_id):
    cursor = db.get_cursor()
    time = datetime.now()
    
    query = '''UPDATE hire_record SET checkout_time = %(checkout_time)s, checkout_staff = %(checkout_staff)s WHERE booking_item_id = %(booking_item_id)s;'''
    cursor.execute(
        query, 
        {
            "booking_item_id": booking_item_id,
            "checkout_time": time,
            "checkout_staff": staff_id,
        }
    )
    if cursor.rowcount == 1:
        return jsonify({'success': True, 'message': 'Success!'})
    else:
        return jsonify({'success': False, 'message': 'Something went wrong'}), 500
    
def confirm_return (machine_id):
    cursor = db.get_cursor()
    query = """UPDATE machine SET status = 3 WHERE machine_id = %(machine_id)s;"""
    cursor.execute(
        query, 
        {
            "machine_id": machine_id,
        }
    )
    if cursor.rowcount == 1:
        return jsonify({'success': True, 'message': 'Success!'})
    else:
        return jsonify({'success': False, 'message': 'Something went wrong'}), 500
    
def record_return(booking_item_id,staff_id):
    cursor = db.get_cursor()
    time = datetime.now()
    
    query = '''UPDATE hire_record SET return_time = %(return_time)s, return_staff = %(return_staff)s WHERE booking_item_id = %(booking_item_id)s;'''
    cursor.execute(
        query, 
        {
            "booking_item_id": booking_item_id,
            "return_time": time,
            "return_staff": staff_id,
        }
    )
    if cursor.rowcount == 1:
        return jsonify({'success': True, 'message': 'Success!'})
    else:
        return jsonify({'success': False, 'message': 'Something went wrong'}), 500
    
def get_bookingItemList(id):
    cursor = db.get_cursor()

    #if id is a array
    if isinstance(id, list):
        booking_items = []

        unique_ids = list(set(id))

        for booking_id in unique_ids:
            query = '''SELECT * FROM 
                        booking_item
                        JOIN machine ON booking_item.machine_id = machine.machine_id
                        JOIN product ON machine.product_code = product.product_code
                    WHERE 
                        booking_id = %(id)s;'''
            cursor.execute(
                query, 
                {
                    "id": booking_id,
                }
            )
            booking_items.extend(cursor.fetchall())
        return booking_items

    # if id is not array
    else:
        query = '''SELECT * FROM 
                    booking_item
                    JOIN machine ON booking_item.machine_id = machine.machine_id
                    JOIN product ON machine.product_code = product.product_code
                WHERE 
                    booking_id = %(id)s'''
        cursor.execute(
            query, 
            {
                "id": id,
            }
        )
        return cursor.fetchall()


def get_booking_by_return_date_and_store(date, store_id):
    cursor = db.get_cursor()
    sql = """
        SELECT b.booking_id, b.customer_id,c.first_name, c.last_name, c.phone, b.create_date,
               bi.booking_item_id, bi.hire_from, bi.hire_to, m.sn, p.name
        FROM booking_item bi
        JOIN booking b ON bi.booking_id = b.booking_id
        JOIN customer c ON b.customer_id = c.customer_id
        JOIN machine m ON bi.machine_id = m.machine_id
        JOIN product p ON m.product_code = p.product_code
        WHERE b.store_id = %s AND DATE(bi.hire_to) = %s
        ORDER BY b.create_date DESC
    """
    cursor.execute(sql, (store_id, date))
    return cursor.fetchall()