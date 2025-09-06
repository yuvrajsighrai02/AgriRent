from eoms.model.db import get_cursor
from flask import jsonify, abort

# Module to hanlde queries related to category table

# Return all active categories order by name
def get_all_active_categories():
    connection  = get_cursor()
    query = """
            SELECT * FROM category
            WHERE status = 1
            ORDER by name;
            """
    connection.execute(query)
    return connection.fetchall()

# Return a category by category code
def get_category_by_code(category_code):
    connection  = get_cursor()
    query = """
            SELECT * FROM category
            WHERE category_code = %(category_code)s;
            """
    connection.execute(query, {'category_code': category_code})
    return connection.fetchone()
    