from eoms.model.db import get_cursor, get_connection
from flask import jsonify, abort
from mysql.connector import Error

# Module to hanlde queries related to cart and cart_item table

# Return a shopping cart by cart_id
def get_cart_by_id(cart_id):
    cursor = get_cursor()
    query = """
            SELECT * FROM cart
            WHERE cart_id = %(cart_id)s;
            """
    cursor.execute(query, {'cart_id': cart_id})
    return cursor.fetchone()

# Return a shopping cart by customer_id
def get_cart_by_customer_id(customer_id):
    cursor = get_cursor()
    query = """
            SELECT * FROM cart
            WHERE customer_id = %(customer_id)s;
            """
    cursor.execute(query, {'customer_id': customer_id})
    return cursor.fetchone()

# Insert a shopping cart, optional parameter customer_id
def add_cart(customer_id=None):
    # This function needs a commit as well
    with get_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            query = """
                    INSERT INTO cart (customer_id)
                    VALUES (%(customer_id)s);
                    """
            cursor.execute(query, {'customer_id': customer_id})
            if cursor.rowcount == 1:
                connection.commit()
                return cursor.lastrowid
            else:
                return None


# Return a list of cart items by cart id
def get_cart_items_by_cart_id(cart_id):
    connection  = get_cursor()
    query = """
            SELECT c.*, 
            p.name, 
            p.image,
            (CEIL(DATEDIFF(c.hire_to, c.hire_from)) * c.hire_rate * c.qty) AS original_subtotal,
            ROUND((CEIL(DATEDIFF(c.hire_to, c.hire_from)) * c.hire_rate * c.qty * (c.disc_rate / 100)), 2) as discount,
            ROUND((CEIL(DATEDIFF(c.hire_to, c.hire_from)) * c.hire_rate * c.qty * (1 - c.disc_rate / 100)), 2) as subtotal
            FROM cart_item c
            INNER JOIN product p ON c.product_code = p.product_code
            WHERE cart_id = %(cart_id)s
            ORDER BY c.line_num;
            """
    connection.execute(query, {'cart_id': cart_id})
    return connection.fetchall()

# Return a cart item by cart item id
def get_cart_item_by_id(cart_item_id):
    connection  = get_cursor()
    query = """
            SELECT c.*, 
            p.name, 
            (CEIL(DATEDIFF(c.hire_to, c.hire_from)) * c.hire_rate * c.qty) AS original_subtotal,
            ROUND((CEIL(DATEDIFF(c.hire_to, c.hire_from)) * c.hire_rate * c.qty * (c.disc_rate / 100)), 2) as discount,
            ROUND((CEIL(DATEDIFF(c.hire_to, c.hire_from)) * c.hire_rate * c.qty * (1 - c.disc_rate / 100)), 2) as subtotal
            FROM cart_item c
            INNER JOIN product p ON c.product_code = p.product_code
            WHERE cart_item_id = %(cart_item_id)s;
            """
    connection.execute(query, {'cart_item_id': cart_item_id})
    return connection.fetchone()

# Add a product to shopping cart
def add_cart_items(cart_id, product_code, qty, hire_from, hire_to):
    # --- THIS IS THE FIX ---
    # Use a managed connection and explicitly commit the transaction.
    try:
        with get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                # Get the next line number
                cursor.execute("SELECT IFNULL(MAX(line_num), 0) + 1 AS next_line FROM cart_item WHERE cart_id = %s", (cart_id,))
                line_num = cursor.fetchone()['next_line']

                # Get the hire rate
                cursor.execute("SELECT price_a FROM product WHERE product_code = %s", (product_code,))
                hire_rate = cursor.fetchone()['price_a']

                # Insert the new item
                query = """
                        INSERT INTO cart_item (cart_id, product_code, qty, line_num, hire_rate, hire_from, hire_to)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """
                cursor.execute(
                    query,
                    (cart_id, product_code, qty, line_num, hire_rate, hire_from, hire_to)
                )
                
                # Commit the changes to the database
                connection.commit()
        return {'status': 'success', 'message': 'Equipment has been added to cart'}
    except Error as e:
        return {'status': 'fail', 'message': str(e)}

# Delete a cart item by cart_item_id
def delete_cart_item_by_id(cart_item_id):
    # --- THIS IS THE FIX ---
    # Use a managed connection and explicitly commit the transaction.
    try:
        with get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                query = """
                        DELETE FROM cart_item
                        WHERE cart_item_id = %(cart_item_id)s;
                        """
                cursor.execute(query, {'cart_item_id': cart_item_id})
                
                if cursor.rowcount == 0:
                    return {'status': 'fail', 'message': 'Cart item not found'}
                else:
                    # Commit the deletion
                    connection.commit()
                    return {'status': 'success', 'message': 'Cart item deleted successfully'}
    except Error as e:
        return {'status': 'fail', 'message': str(e)}

# Remove any cart items hire date of which is in the past
def delete_outdated_cart_items_by_cart_id(cart_id):
    # --- THIS IS THE FIX ---
    # Use a managed connection and explicitly commit the transaction.
    try:
        with get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                query = """
                        DELETE FROM cart_item
                        WHERE cart_id = %(cart_id)s
                        AND hire_from < NOW();
                        """
                cursor.execute(query, {'cart_id': cart_id})
                rowcount = cursor.rowcount
                # Commit the deletion if any rows were affected
                if rowcount > 0:
                    connection.commit()
                return rowcount
    except Error as e:
        print(f"Error deleting outdated cart items: {e}")
        return 0


# Update cart item qty, hire_from, hire_to by cart item id
def update_cart_item_by_id(cart_item_id, **kwargs):
    # --- THIS IS THE FIX ---
    # Use a managed connection and explicitly commit the transaction.
    allowed_params = ['qty', 'hire_from', 'hire_to']
    update_parts = []
    
    for key, value in kwargs.items():
        if key in allowed_params:
            update_parts.append(f"{key} = %({key})s")
    
    if not update_parts:
        return # No valid fields to update

    update_string = ", ".join(update_parts)
    query = f"UPDATE cart_item SET {update_string} WHERE cart_item_id = %(cart_item_id)s;"
    
    params = kwargs
    params['cart_item_id'] = cart_item_id
    
    try:
        with get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                # Commit the update
                connection.commit()
    except Error as e:
        print(f"Error updating cart item: {e}")


# Calculate original total, total dicount, and discounted total for given cart items
def get_cart_items_totals(cart_items: dict):
    original_total = round(sum(item['original_subtotal'] for item in cart_items), 2)
    total_discount = round(sum(item['discount'] for item in cart_items), 2)
    cart_total = round(sum(item['subtotal'] for item in cart_items), 2)
    total_gst =  round(cart_total * 3 / 23, 2)
    return original_total, total_discount, cart_total, total_gst

# Apply discount to eligible cart items and return the number of rows affected
def apply_promo_to_cart(cart_id, promo_code):
    try:
        with get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                query = """
                    UPDATE cart_item ci
                    JOIN (
                        SELECT pp.product_code, p.disc_rate
                        FROM promo_product pp
                        JOIN promotion p ON pp.promo_code = p.promo_code
                        WHERE p.promo_code = %(promo_code)s 
                        AND p.start_date <= NOW() 
                        AND p.end_date >= NOW()
                        AND p.status = 1
                    ) AS promo
                    ON ci.product_code = promo.product_code
                    SET ci.disc_rate = promo.disc_rate
                    WHERE ci.cart_id = %(cart_id)s;
                    """
                cursor.execute(query, {'cart_id': cart_id, 'promo_code': promo_code})
                rowcount = cursor.rowcount

                if rowcount > 0:
                    query = """
                    UPDATE cart
                    SET promo_code = %(promo_code)s
                    WHERE cart_id = %(cart_id)s;
                    """
                    cursor.execute(query, {'cart_id': cart_id, 'promo_code': promo_code})
                
                connection.commit()
                return rowcount
    except Error as e:
        print(f"Error applying promo: {e}")
        return 0

# Delete promo from cart and cart items
def delete_promo_by_cart_id(cart_id):
    try:
        with get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                # Remove promo from cart
                cursor.execute("UPDATE cart SET promo_code = NULL WHERE cart_id = %s;", (cart_id,))
                rowcount = cursor.rowcount
                # Remove discount from cart items
                cursor.execute("UPDATE cart_item SET disc_rate = 0 WHERE cart_id = %s;", (cart_id,))
                rowcount += cursor.rowcount
                connection.commit()
                return rowcount
    except Error as e:
        print(f"Error deleting promo: {e}")
        return 0
