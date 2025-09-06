from eoms.model.db import get_cursor
from flask import jsonify, abort
import eoms.model.db as db

# Module to hanlde queries related to store table

# Return all active stores order by name
def get_all_active_stores():
    connection  = get_cursor()
    query = """
            SELECT * FROM store
            WHERE status = 1
            ORDER by store_name;
            """
    connection.execute(query)
    return connection.fetchall()

# Return a store by store id
def get_store_by_code(stores_id):
    connection  = get_cursor()
    query = """
            SELECT * FROM store
            WHERE store_id = %(stores_id)s;
            """
    connection.execute(query, {'stores_id': stores_id})
    return connection.fetchone()
    
    #get all info from store table
def select_all_from_store():
    cursor = db.get_cursor()
    query = '''SELECT *
                FROM store;'''
    
    cursor.execute(
        query, 
        )
    return cursor.fetchall()