from eoms.model.db import get_cursor
from flask import jsonify, abort
from datetime import datetime
import eoms.model.db as db

# Module to hanlde queries related to product table

# Return all active products by category code order by name
def get_products_by_categroy(category_code):
    connection  = get_cursor()
    query = """
            SELECT * FROM product
            WHERE (category_code = %(category_code)s OR %(category_code)s IS NULL)
            AND status = 1
            ORDER by name;
            """
    connection.execute(query, {'category_code': category_code})
    return connection.fetchall()

# Return a products by product code
def get_product_by_code(product_code):
    connection  = get_cursor()
    query = """
            SELECT * FROM product
            WHERE product_code = %(product_code)s;
            """
    connection.execute(query, {'product_code': product_code})
    return connection.fetchone()

    #get all info from product table
def select_all_from_product():
    cursor = db.get_cursor()
    query = '''SELECT *
                FROM product;'''
    
    cursor.execute(
        query, 
        )
    return cursor.fetchall()



# Update product info in db
def add_new_equipment(
        product_code,
        sn,
        store_id,
        purchase_date,
        cost
):
    cursor = db.get_cursor()
    
    query = """INSERT INTO machine ( product_code, sn, store_id, purchase_date, cost)
            VALUES(%(product_code)s, %(sn)s, %(store_id)s, %(purchase_date)s, %(cost)s);
            """
    cursor.execute(
        query,
        {
            "product_code": product_code,
            "sn": sn,
            "store_id": store_id,
            "purchase_date": purchase_date,
            "cost": cost
        }
    )
    
    if cursor.rowcount == 1:
        new_id = cursor.lastrowid 
        return new_id
    else:
        return jsonify({'error': 'Something went wrong'}), 500
    
def select_3_rand_products():
    cursor = db.get_cursor()
    query = """SELECT * FROM product ORDER BY RAND() LIMIT 3;"""
    cursor.execute(query)
    return cursor.fetchall()

def select_4_rand_products():
    cursor = db.get_cursor()
    query = """SELECT * FROM product ORDER BY RAND() LIMIT 4;"""
    cursor.execute(query)
    return cursor.fetchall()
    
# Search product by name or description
def search_product_by_name_desc(search_term):
    cursor = get_cursor()
    query = """
            SELECT *
            FROM product
            WHERE (`name` LIKE CONCAT('%', %(search_term)s, '%') OR `desc` LIKE CONCAT('%', %(search_term)s, '%'))
            AND status = 1
            ORDER BY name;
            """
    cursor.execute(query, {'search_term': search_term})
    return cursor.fetchall()