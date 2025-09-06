from eoms import app
from flask import render_template, request, session
from eoms.model import db, stock
from eoms.model.session_utils import allow_role
from datetime import datetime


@app.route('/view_inventory', methods=['GET', 'POST'])
@allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
def view_inventory():
    product_code = request.form.get('product_code', '').strip()
    category_code = request.form.get('category_code', '').strip()
    product_name = request.form.get('product_name', '').strip()
    
    role = session['role']
    store_id = session.get('store_id') if role in ['staff', 'lmgr'] else request.form.get('store_id', '').strip()

    # Fetching products
    product_list = get_products(product_code, category_code, product_name, store_id)
    
    inventory_list = []
    processed_products = set()

    for product in product_list:
        p_code = product['product_code']
        
        # For national view (no store_id filter), process each product only once
        if not store_id and p_code in processed_products:
            continue

        p_store_id = product.get('store_id') if store_id else None

        if p_store_id:
            total_qty = stock.get_total_quantity(p_code, p_store_id)
            # Use the new function for a simple 'active' count
            in_stock_qty = stock.get_current_in_stock_count(p_code, p_store_id)
            store_name = product.get('store_name', 'N/A')
        else: # National level view
            total_qty = stock.get_total_quantity(p_code)
            # Use the new function for a simple 'active' count
            in_stock_qty = stock.get_current_in_stock_count(p_code)
            store_name = 'All Stores'
            processed_products.add(p_code)

        inventory_list.append({
            'product_code': p_code,
            'c_name': product['category_name'],
            'p_name': product['name'],
            'store_name': store_name,
            'total_machine_quantities': total_qty,
            'in_stock': in_stock_qty,
        })
        
    category_list = get_category()
    store_list = get_stores()

    return render_template('staff_product/inventory.html', 
                           inventory_list=inventory_list,
                           category_list=category_list,
                           store_list=store_list,
                           store_id_filter=store_id,
                           product_code_filter=product_code,
                           category_code_filter=category_code,
                           product_name_filter=product_name)


# This function now counts all machines except retired ones.
def count_machine_quantities(product_code, store_id):
    """Counts all machines for a specific product and store with status Active, On Hire, Returned and Damaged."""
    sql = '''
        SELECT COUNT(product_code) 
        FROM machine 
        WHERE product_code = %s 
        AND store_id = %s
        AND status IN (0, 1, 2, 3);
    '''
    cursor = db.get_cursor()
    cursor.execute(sql, (product_code, store_id,))
    number = cursor.fetchone()
    return number

# This function now counts all machines except retired ones nationally.
def count_national_machine_quantities(product_code):
    """Counts all machines for a specific product nationally with status Active, On Hire, Returned and Damaged."""
    sql = '''
        SELECT COUNT(product_code) 
        FROM machine 
        WHERE product_code = %s
        AND status IN (0, 1, 2, 3);
    '''
    cursor = db.get_cursor()
    cursor.execute(sql, (product_code,))
    number = cursor.fetchone()
    return number


# New function to count only active machines for in-stock calculation.
def count_active_machines(product_code, store_id):
    """Counts the number of active machines for a specific product and store."""
    sql = '''
        SELECT COUNT(product_code) 
        FROM machine 
        WHERE product_code = %s 
        AND store_id = %s
        AND status = 1;
    '''
    cursor = db.get_cursor()
    cursor.execute(sql, (product_code, store_id,))
    number = cursor.fetchone()
    return number


# New function to count only active machines nationally.
def count_national_active_machines(product_code):
    """Counts the number of active machines for a specific product nationally."""
    sql = '''
        SELECT COUNT(product_code) 
        FROM machine 
        WHERE product_code = %s
        AND status = 1;
    '''
    cursor = db.get_cursor()
    cursor.execute(sql, (product_code,))
    number = cursor.fetchone()
    return number


# Helper functions for fetching products, categories, and stores
def get_products(product_code=None, category_code=None, product_name=None, store_id=None):
    params = []
    sql = """
        SELECT DISTINCT p.product_code, p.name, c.name AS category_name, m.store_id, s.store_name
        FROM product p
        JOIN category c ON p.category_code = c.category_code
        LEFT JOIN machine m ON p.product_code = m.product_code
        LEFT JOIN store s ON m.store_id = s.store_id
        WHERE 1=1
    """
    if product_code:
        sql += ' AND p.product_code = %s'
        params.append(product_code)
    if category_code:
        sql += ' AND p.category_code = %s'
        params.append(category_code)
    if product_name:
        sql += ' AND p.name LIKE %s'
        params.append(f'%{product_name}%')
    if store_id:
        sql += ' AND m.store_id = %s'
        params.append(store_id)
    
    cursor = db.get_cursor()
    cursor.execute(sql, tuple(params))
    return cursor.fetchall()

def get_category():
    cursor = db.get_cursor()
    cursor.execute("SELECT * FROM category")
    return cursor.fetchall()

def get_stores():
    cursor = db.get_cursor()
    cursor.execute("SELECT * FROM store")
    return cursor.fetchall()


def get_today_inventory(product_code=None, store_id=None):
    params = []
    selected_date = request.form.get('selected_date')
    if selected_date is None:
        selected_date = datetime.now().date()
    else:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    sql = '''
        SELECT COUNT(DISTINCT bi.machine_id) 
        FROM booking b
        INNER JOIN booking_item bi ON b.booking_id = bi.booking_id
        INNER JOIN machine m ON bi.machine_id = m.machine_id
        WHERE m.status IN (0, 1, 2, 3)
    '''
    if product_code:
        sql += ' AND m.product_code = %s'
        params.append(product_code)
    if store_id:
        sql += ' AND m.store_id = %s'
        params.append(store_id)

    # Corrected `b.hire_from` to `bi.hire_from`
    sql += ' AND bi.hire_from <= %s AND bi.hire_to >= %s;'
    params.append(selected_date)
    params.append(selected_date)

    cursor = db.get_cursor()
    cursor.execute(sql, tuple(params))
    number = cursor.fetchone()
    return number


def get_total_quantities_and_instock(product_code):
    sql_total = '''SELECT COUNT(product_code) FROM machine WHERE product_code = %s;'''
    cursor = db.get_cursor()
    cursor.execute(sql_total, (product_code,))
    total_quantities = cursor.fetchone()

    sql_instock = '''SELECT COUNT(product_code) FROM machine WHERE product_code = %s AND status = '1';'''
    cursor.execute(sql_instock, (product_code,))
    in_stock = cursor.fetchone()

    return {'total_quantities': total_quantities['COUNT(product_code)'], 'in_stock': in_stock['COUNT(product_code)']}


def get_available_machine(product_code, store_id):
    sql = '''
        SELECT machine_id, sn FROM machine 
        WHERE product_code = %s AND store_id = %s AND status = 1;
    '''
    cursor = db.get_cursor()
    cursor.execute(sql, (product_code, store_id,))
    available_machine_list = cursor.fetchall()
    return available_machine_list


def get_booked_item():
    sql = ''' SELECT b.*, bi.* FROM booking b
              INNER JOIN booking_item bi ON b.booking_id = bi.booking_id;'''
    cursor = db.get_cursor()
    cursor.execute(sql)
    return cursor.fetchall()


# New for In Stock for Equipment detail page 
def get_in_stock(product_code, store_id, hire_from, hire_to):
    # Total available machines at the specific store
    total_quantities_sql = '''SELECT COUNT(product_code) FROM machine WHERE product_code = %s AND store_id = %s AND status IN (1, 2, 3);'''
    cursor = db.get_cursor()
    cursor.execute(total_quantities_sql, (product_code, store_id,))
    total_quantities = cursor.fetchone()['COUNT(product_code)']
    
    # Machines already booked during the selected period
    booked_count_sql = '''
        SELECT COUNT(bi.machine_id)
        FROM booking_item bi
        JOIN booking b ON bi.booking_id = b.booking_id
        JOIN machine m ON bi.machine_id = m.machine_id
        WHERE m.product_code = %s AND m.store_id = %s AND b.status IN ('Confirmed', 'Paid') AND m.status IN (0, 1, 2, 3)
        AND (bi.hire_from <= %s AND bi.hire_to >= %s);
    '''
    cursor.execute(booked_count_sql, (product_code, store_id, hire_to, hire_from,))
    booked_count = cursor.fetchone()['COUNT(bi.machine_id)']

    in_stock_count = total_quantities - booked_count
    return in_stock_count


def get_in_stock_for_products(product_code, store_id, hire_from, hire_to):
    sql = '''
        SELECT COUNT(p.product_code)
        FROM product p
        LEFT JOIN machine m ON p.product_code = m.product_code
        WHERE p.product_code = %s AND m.store_id = %s
          AND m.status IN (0, 1, 2, 3) 
          AND m.machine_id NOT IN (
            SELECT bi.machine_id
            FROM booking_item bi
            JOIN booking b ON bi.booking_id = b.booking_id
            WHERE (b.hire_from BETWEEN %s AND %s OR b.hire_to BETWEEN %s AND %s) AND b.status IN ('Confirmed', 'Paid')
          );
    '''
    cursor = db.get_cursor()
    cursor.execute(sql, (product_code, store_id, hire_from, hire_to, hire_from, hire_to))
    in_stock_count = cursor.fetchone()

    return in_stock_count['COUNT(p.product_code)']


def check_product_in_stock(product_code, store_id, quantity, hire_from, hire_to):
    in_stock_count = get_in_stock_for_products(product_code, store_id, hire_from, hire_to)
    if in_stock_count >= quantity:
        return True
    return False

