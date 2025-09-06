from eoms import app
from flask import session
from eoms.model import category, cart, db # Import the db object

# This module handles global variables that can be used in the base templates

@app.context_processor
def inject_category_options():
    """Makes the list of equipment categories available to all templates."""
    category_options = category.get_all_active_categories()
    return dict(category_options=category_options)

@app.context_processor
def inject_cart_item_count():
    """Makes the number of items in the cart available to all templates."""
    cart_item_count = 0
    if session.get('cart_id'):
        cart_items = cart.get_cart_items_by_cart_id(session['cart_id'])
        if cart_items:
            cart_item_count = len(cart_items)
    return dict(cart_item_count=cart_item_count)

@app.context_processor
def inject_cart_notifications_count():
    """
    Makes the number of unread messages available to all templates.
    This new version works with our threaded messaging system for both
    customers and staff.
    """
    notifications_count = 0
    if session.get('loggedin'):
        role = session.get('role')
        cursor = None
        try:
            cursor = db.get_cursor()
            # If the user is a customer, count their unread threads
            if role == 'customer':
                customer_id = session.get('customer_id')
                if customer_id:
                    sql = "SELECT COUNT(*) as count FROM message_threads WHERE customer_id = %s AND customer_unread = TRUE"
                    cursor.execute(sql, (customer_id,))
                    result = cursor.fetchone()
                    if result:
                        notifications_count = result['count']
            # If the user is staff, count unread threads for their store
            else:
                store_id = session.get('store_id')
                if store_id:
                    sql = "SELECT COUNT(*) as count FROM message_threads WHERE store_id = %s AND staff_unread = TRUE"
                    cursor.execute(sql, (store_id,))
                    result = cursor.fetchone()
                    if result:
                        notifications_count = result['count']
        except Exception as e:
            print(f"Error getting notification count: {e}")
            notifications_count = 0
        finally:
            if cursor:
                cursor.close()

    return dict(notifications_count=notifications_count)
