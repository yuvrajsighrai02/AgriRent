from eoms import app
from flask import render_template, redirect, request, flash, url_for,session,jsonify
from eoms.model import db
from eoms.model.session_utils import allow_role
import json
import bcrypt

# ==============================================================================
# STORE MANAGEMENT ROUTES
# ==============================================================================
# store list view  
@app.route('/admin/stores', methods=['GET', 'POST'])
def stores():
    allow_role(['nmgr', 'admin'])
    store_name = request.form.get('store_name', '').strip()
    store_list = get_stores(store_name)
    return render_template('administration/stores.html', store_list = store_list, store_name = store_name)

# store add and edit   
@app.route('/manage_store', methods=['POST'])
def manage_store():
    allow_role(['nmgr', 'admin'])
    store_id = request.form['store_id']
    store_name = request.form['store_name'].strip()
    phone = request.form['phone'].strip()
    email = request.form['email'].strip()
    address_line1 = request.form['address_line1'].strip()
    city = request.form['city'].strip()
    response = None
    
    # Check if the store already exists to decide between add or edit
    if store_id:
        if not check_exist_store(store_name, store_id):
            response = update_store(store_id, store_name, phone, email, address_line1, city)
        else:
            response = {'success': False, 'message': 'Store Name Exists'}
            return jsonify(response)
    else:
        if not check_exist_store(store_name):
            response = add_store(store_name, phone, email, address_line1, city)
        else:
            response = {'success': False, 'message': 'Store Name Exists'}
            return jsonify(response)

    if response['success']:
        flash(response['message'], 'success')
    else:
        flash(response['message'], 'danger')
        
    return jsonify(response)


# store delete
@app.route('/delete_store', methods=['POST'])
def delete_store():
    store_id = request.form['store_id']
    response = delete_store_by_id(store_id)
    if response['success']:
        flash(response['message'], 'success')
    else:
        flash(response['message'], 'danger')
    return redirect(url_for('stores'))

# ==============================================================================
# STAFF MANAGEMENT ROUTES
# ==============================================================================

@app.route('/staff', methods=['GET', 'POST'])
def staff():
    allow_role(['lmgr','nmgr', 'admin'])
    first_name = request.values.get('first_name', '').strip()
    last_name = request.values.get('last_name', '').strip()
    
    role = session.get('role')
    store_list = []
    selected_store_id = ''

    if role in ['nmgr', 'admin']:
        store_list = get_stores()
        selected_store_id = request.values.get('store_id', '')
    else:
        selected_store_id = session.get('store_id')

    staff_list = get_staff(first_name, last_name, selected_store_id)
    
    return render_template(
        'administration/staff.html', 
        staff_list=staff_list, 
        store_list=store_list, 
        first_name=first_name,
        last_name=last_name, 
        store_id=selected_store_id
    )

@app.route('/manage_staff', methods=['POST'])
def manage_staff():
    allow_role(['lmgr', 'nmgr', 'admin'])
    staff_id = request.form['staff_id'].strip()
    first_name = request.form['first_name'].strip()
    last_name = request.form['last_name'].strip()
    phone = request.form['phone'].strip()
    position = request.form['position'].strip()
    is_active = int(request.form['is_active'].strip())
    role = request.form['role'].strip()
    email = request.form['email'].strip()
    user_id = request.form['user_id'].strip()
    
    login_role = session.get('role')
    if login_role == 'lmgr':
        store_id = session.get('store_id')
    else:
        store_id = request.form.get('store_id', '').strip()

    response = None
    if staff_id:
        response = update_staff(staff_id, store_id, first_name, last_name, position, phone, role, is_active, user_id) 
    else:
        user_id = get_max_user_id()
        default_pwd = 'Test1234!'
        hashed_password = bcrypt.hashpw(default_pwd.encode('utf-8'), bcrypt.gensalt())
        response = add_staff(user_id, email, hashed_password, role, is_active, store_id, first_name, last_name, position, phone)

    if response['success']:
        flash(response['message'], 'success')
    else:
        flash(response['message'], 'danger')
        
    return jsonify(response)

# ==============================================================================
# CUSTOMER MANAGEMENT ROUTES (UPDATED LOGIC)
# ==============================================================================

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    """
    Displays the customer management page with role-based filtering.
    - Staff/Local Managers see customers associated with their store.
    - National Managers & Admins can see all customers and filter by store.
    """
    allow_role(['staff','lmgr','nmgr', 'admin'])
    
    # Get search filters from the form for both GET and POST requests
    first_name = request.values.get('first_name', '').strip()
    last_name = request.values.get('last_name', '').strip()
    
    role = session.get('role')
    store_list = []
    selected_store_id = ''

    # National Managers and Admins can see all stores and have a filter dropdown
    if role in ['nmgr', 'admin']:
        store_list = get_stores()  # Fetch all stores for the filter dropdown
        selected_store_id = request.values.get('store_id', '')
    
    # Staff and Local Managers are automatically filtered by their assigned store
    else:  # role is 'staff' or 'lmgr'
        selected_store_id = session.get('store_id')

    # Fetch the list of customers using the determined filters
    customer_list = get_customers(first_name, last_name, selected_store_id)
    
    return render_template(
        'administration/customers.html', 
        customer_list=customer_list, 
        store_list=store_list, 
        first_name=first_name,
        last_name=last_name, 
        store_id=selected_store_id  # Pass store_id back to pre-select the filter
    )


@app.route('/manage_customer', methods=['POST'])
def manage_customer():
    allow_role(['lmgr', 'nmgr', 'admin'])
    customer_id = request.form['customer_id'].strip()
    first_name = request.form['first_name'].strip()
    last_name = request.form['last_name'].strip()
    phone = request.form['phone'].strip()
    address_line1 = request.form['address_line1'].strip()
    city = request.form['city'].strip()
    status = request.form['status'].strip()
    is_active = int(status)
    user_id = request.form['user_id'].strip()
    response = update_customer(customer_id, first_name, last_name, phone, address_line1,  city,  is_active, user_id)

    if response['success']:
        flash(response['message'], 'success')
    else:
        flash(response['message'], 'danger')
        
    return jsonify(response)

# ==============================================================================
# HELPER FUNCTIONS (DATABASE LOGIC)
# ==============================================================================

# --- Store Helpers ---
def get_stores(store_name=None):
    params = []
    sql = 'SELECT * FROM store WHERE 1=1'    
    if store_name:
        sql += ' AND store_name LIKE %s'
        params.append(f'%{store_name}%')     
    sql += ' ORDER BY store_name;'     
    cursor = db.get_cursor()   
    cursor.execute(sql, params)  
    return cursor.fetchall() 

# --- Store Helpers (with commit + better error handling) ---
def add_store(store_name, phone, email, address_line1, city):
    try:
        sql = '''
            INSERT INTO store (store_name, phone, email, address_line1, city)
            VALUES (%s, %s, %s, %s, %s);
        '''
        cursor = db.get_cursor()
        cursor.execute(sql, (store_name, phone, email, address_line1, city))
        db.connection.commit()   # Commit transaction ✅
        return {'success': True, 'message': 'Store added successfully'}
    except Exception as err:
        return {'success': False, 'message': f'Error adding store: {err}'}


def update_store(store_id, store_name, phone, email, address_line1, city):
    try:
        sql = '''
            UPDATE store
            SET store_name = %s, phone = %s, email = %s, address_line1 = %s, city = %s
            WHERE store_id = %s;
        '''
        cursor = db.get_cursor()
        cursor.execute(sql, (store_name, phone, email, address_line1, city, store_id))
        db.connection.commit()   # Commit transaction ✅
        return {'success': True, 'message': 'Store updated successfully'}
    except Exception as err:
        return {'success': False, 'message': f'Error updating store: {err}'}


def delete_store_by_id(store_id):
    try:
        sql = 'DELETE FROM store WHERE store_id = %s;'
        cursor = db.get_cursor()
        cursor.execute(sql, (store_id,))
        db.connection.commit()   # Commit transaction ✅
        return {'success': True, 'message': 'Store deleted successfully'}
    except Exception as err:
        if 'FOREIGN KEY' in str(err):
            return {'success': False, 'message': 'This store is in use. It cannot be deleted!'}
        return {'success': False, 'message': f'Error deleting store: {err}'}
 

def check_exist_store(store_name, store_id = None):
    params = []
    sql = 'SELECT COUNT(*) AS NUM FROM store WHERE store_name = %s'   
    params.append(store_name)  
    if store_id:
        sql +=' AND store_id != %s' 
        params.append(store_id)   
    cursor = db.get_cursor()   
    cursor.execute(sql, params)  
    count = cursor.fetchone()['NUM']
    return count > 0

# --- Staff Helpers ---

#New for all admin n m and staffs
# def get_staff(first_name=None, last_name=None, store_id=None):
#     params = []
#     query = """
#         SELECT s.*, st.store_name, u.email, u.is_active, u.role 
#         FROM staff s 
#         JOIN user u ON u.user_id = s.user_id
#         LEFT JOIN store st ON st.store_id = s.store_id
#         WHERE 1=1
#     """
#     if first_name:
#         query += ' AND s.first_name LIKE %s'
#         params.append(f'%{first_name}%')
#     if last_name:
#         query += ' AND s.last_name LIKE %s'
#         params.append(f'%{last_name}%')   
#     if store_id:
#         query += ' AND s.store_id = %s'
#         params.append(store_id)    
#     query += ' ORDER BY st.store_name, s.first_name, s.last_name;'     
#     cursor = db.get_cursor()   
#     cursor.execute(query, params)  
#     return cursor.fetchall() 


#old for show only Branch Staffs
def get_staff(first_name = None, last_name = None, store_id  = None):
     params = []
     sql = '''SELECT staff.*,store.store_name,user.email,user.is_active,user.role FROM staff 
                INNER JOIN store ON staff.store_id=store.store_id 
                INNER JOIN user ON user.user_id=staff.user_id
                WHERE 1=1'''    
     if first_name:
        sql += ' AND staff.first_name LIKE %s'
        params.append(f'%{first_name}%')
     if last_name:
        sql += ' AND staff.last_name LIKE %s'
        params.append(f'%{last_name}%')   
     if store_id:
        sql += ' AND staff.store_id = %s'
        params.append(store_id)    
     sql += ' ORDER BY staff.store_id,staff.first_name,staff.last_name;'     
     cursor = db.get_cursor()   
     cursor.execute(sql, params)  
     return cursor.fetchall() 


def get_max_user_id():
    sql = 'SELECT MAX(user_id) AS max_id FROM user;'        
    cursor = db.get_cursor()   
    cursor.execute(sql)  
    result = cursor.fetchone()
    return (int(result['max_id']) + 1) if result and result['max_id'] else 1

def add_staff(user_id, email, password, role, is_active, store_id, first_name, last_name, position, phone): 
    try: 
        cursor = db.get_cursor()
        # Insert into user table
        sql_user = """
            INSERT INTO user (user_id, email, password, role, is_active)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(sql_user, (user_id, email, password, role, is_active))

        # Insert into staff table
        sql_staff = """
            INSERT INTO staff (user_id, store_id, first_name, last_name, position, phone)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(sql_staff, (user_id, store_id, first_name, last_name, position, phone))

        db.connection.commit()   # ✅ Commit transaction
        return {'success': True, 'message': 'Staff added successfully'}

    except Exception as err:
        db.connection.rollback()  # Roll back on failure
        return {'success': False, 'message': f'Error adding staff: {err}'}


def update_staff(staff_id, store_id, first_name, last_name, position, phone, role, is_active, user_id): 
    try:
        cursor = db.get_cursor()

        # Update user role and status
        sql_user = """
            UPDATE user SET role = %s, is_active = %s WHERE user_id = %s;
        """
        cursor.execute(sql_user, (role, is_active, user_id))

        # Update staff info
        sql_staff = """
            UPDATE staff 
            SET store_id = %s, first_name = %s, last_name = %s, position = %s, phone = %s 
            WHERE staff_id = %s;
        """
        cursor.execute(sql_staff, (store_id, first_name, last_name, position, phone, staff_id))

        db.connection.commit()   # ✅ Commit transaction
        return {'success': True, 'message': 'Staff updated successfully'}

    except Exception as err:
        db.connection.rollback()  # Roll back on failure
        return {'success': False, 'message': f'Error updating staff: {err}'}


# Old
# # --- Customer Helpers (UPDATED LOGIC) ---
# def get_customers(first_name=None, last_name=None, store_id=None):
#     """
#     Fetches a list of customers with flexible filtering.
#     - Uses LEFT JOIN to include customers who may not have a preferred store.
#     - Filters by name and store ID.
#     """
#     params = []
#     # Using LEFT JOIN on store ensures all customers are shown, even if my_store is NULL.
#     sql = """
#         SELECT c.*, s.store_name, u.email, u.is_active, u.role 
#         FROM customer c 
#         JOIN user u ON u.user_id = c.user_id
#         LEFT JOIN store s ON c.my_store = s.store_id 
#         WHERE 1=1
#     """ 
#     if first_name:
#         sql += ' AND c.first_name LIKE %s'
#         params.append(f'%{first_name}%')
#     if last_name:
#         sql += ' AND c.last_name LIKE %s'
#         params.append(f'%{last_name}%')   
#     if store_id:
#         sql += ' AND c.my_store = %s'
#         params.append(store_id)    
    
#     sql += ' ORDER BY s.store_name, c.first_name, c.last_name;'     
#     cursor = db.get_cursor()   
#     cursor.execute(sql, params)  
#     return cursor.fetchall() 

# def add_customer(user_id, email, password, first_name, last_name, phone, address_line1, city, store_id): 
#     sql = 'INSERT INTO user (user_id, email, password, role, is_active) VALUES (%s, %s, %s, "customer", 1);'    
#     cursor = db.get_cursor()    
#     cursor.execute(sql,(user_id, email, password))
#     sql = 'INSERT INTO customer (user_id, first_name, last_name, phone, address_line1, city, my_store) VALUES (%s, %s, %s, %s, %s, %s, %s);'    
#     cursor = db.get_cursor()    
#     cursor.execute(sql,(user_id, first_name, last_name, phone, address_line1, city, store_id))  
#     return cursor.fetchone()

# def update_customer(customer_id, first_name, last_name, phone, address_line1, city,is_active, user_id): 
#     try:
#         sql = 'UPDATE customer SET first_name = %s, last_name = %s, phone = %s, address_line1 = %s, city = %s WHERE customer_id = %s;'    
#         cursor = db.get_cursor()    
#         cursor.execute(sql,(first_name, last_name, phone, address_line1, city, customer_id))  
#         sql = 'UPDATE user SET is_active = %s WHERE user_id = %s;'    
#         cursor = db.get_cursor()    
#         cursor.execute(sql,(is_active, user_id))  
#         return {'success': True, 'message': 'Customer Edited Successfully'}
#     except Exception as err:
#         return {'success': False, 'message': 'Something went wrong'}



#New
# --- Customer Helpers (Corrected) ---
def get_customers(first_name=None, last_name=None, store_id=None):
    """
    Fetches a list of customers with flexible filtering.
    - Uses LEFT JOIN to include customers who may not have a preferred store.
    - Filters by name and store ID.
    """
    params = []
    sql = """
        SELECT c.*, s.store_name, u.email, u.is_active, u.role 
        FROM customer c 
        JOIN user u ON u.user_id = c.user_id
        LEFT JOIN store s ON c.my_store = s.store_id 
        WHERE 1=1
    """ 
    if first_name:
        sql += ' AND c.first_name LIKE %s'
        params.append(f'%{first_name}%')
    if last_name:
        sql += ' AND c.last_name LIKE %s'
        params.append(f'%{last_name}%')   
    if store_id:
        sql += ' AND c.my_store = %s'
        params.append(store_id)    
    
    sql += ' ORDER BY s.store_name, c.first_name, c.last_name;'     
    cursor = db.get_cursor()   
    cursor.execute(sql, params)  
    return cursor.fetchall() 


def add_customer(user_id, email, password, first_name, last_name, phone, address_line1, city, store_id): 
    try:
        cursor = db.get_cursor()
        # Insert into user
        sql_user = """
            INSERT INTO user (user_id, email, password, role, is_active)
            VALUES (%s, %s, %s, 'customer', 1);
        """
        cursor.execute(sql_user, (user_id, email, password))

        # Insert into customer
        sql_customer = """
            INSERT INTO customer (user_id, first_name, last_name, phone, address_line1, city, my_store)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(sql_customer, (user_id, first_name, last_name, phone, address_line1, city, store_id))

        db.connection.commit()   # ✅ Commit transaction
        return {'success': True, 'message': 'Customer added successfully'}

    except Exception as err:
        db.connection.rollback()  # rollback on failure
        return {'success': False, 'message': f'Error adding customer: {err}'}


def update_customer(customer_id, first_name, last_name, phone, address_line1, city, is_active, user_id): 
    try:
        cursor = db.get_cursor()

        # Update customer info
        sql_customer = """
            UPDATE customer 
            SET first_name = %s, last_name = %s, phone = %s, address_line1 = %s, city = %s
            WHERE customer_id = %s;
        """
        cursor.execute(sql_customer, (first_name, last_name, phone, address_line1, city, customer_id))

        # Update user active status
        sql_user = "UPDATE user SET is_active = %s WHERE user_id = %s;"
        cursor.execute(sql_user, (is_active, user_id))

        db.connection.commit()   # ✅ Commit transaction
        return {'success': True, 'message': 'Customer updated successfully'}

    except Exception as err:
        db.connection.rollback()
        return {'success': False, 'message': f'Error updating customer: {err}'}
