from eoms.model.db import get_cursor
from flask import jsonify, abort
from datetime import datetime


# Module to hanlde queries related to promition and promo_product table

# Get current active promo code, it can be used for validation
def get_current_promo_by_code(promo_code):
    cursor = get_cursor
    query = """
            SELECT * FROM promotion
            WHERE promo_code = %(promo_code)s
            AND start_date <= NOW() 
            AND end_date >= NOW()
            AND status = 1
            ;
            """
    cursor.execute(query, {'promo_code': promo_code})
    return cursor.fetchone()


# Validate promo code for given cart id
def validate_promo_code_in_cart(promo_code, cart_id):
    cursor  = get_cursor()
    query = """
            SELECT COUNT(*) FROM cart_item ci AS count
            INNER JOIN promo_product pp ON pp.product_code = cart_item.product_code
            WHERE ci.cart_id = %(cart_id)s
            AND pp.promo_code = %(promo_code)s
            ;
            """
    cursor.execute(
        query, 
        {
            'cart_id': cart_id,
            'promo_code': promo_code,
            }
        )
    return cursor.fetchone()['count']


# Get current promotion
def get_all_current_promo():
    cursor = get_cursor()
    query = """
            SELECT * FROM promotion
            WHERE 1 = 1
            AND start_date <= NOW() 
            AND end_date >= NOW()
            AND status = 1
            ORDER BY disc_rate DESC
            ;
            """
    cursor.execute(query)
    return cursor.fetchall()


# Get products currently on promotion
def get_products_on_promo():
    cursor = get_cursor()
    query = """
            SELECT * FROM product p
            INNER JOIN promo_product pp ON pp.product_code = p.product_code
            INNER JOIN promotion pr on pr.promo_code = pp.promo_code
            WHERE 1 = 1
            AND pr.start_date <= NOW() 
            AND pr.end_date >= NOW()
            AND pr.status = 1
            ;
            """
    cursor.execute(query)
    return cursor.fetchall()


# Get products by promo code
def get_products_by_promo_code(promo_code):
    cursor = get_cursor()
    query = """
            SELECT * FROM product p
            INNER JOIN promo_product pp ON pp.product_code = p.product_code
            WHERE 1 = 1
            AND pp.promo_code = %(promo_code)s -- FIX: Specify pp.promo_code to remove ambiguity
            ;
            """
    cursor.execute(query, {'promo_code': promo_code})
    return cursor.fetchall()
