from eoms import app
from flask import render_template, redirect, request, flash, url_for,session,jsonify
from eoms.model import db
from eoms.model.session_utils import allow_role
from eoms.model.upload import upload_product_image

@app.route('/products', methods=['GET', 'POST'])
def products():
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    product_code = request.form.get('product_code', '').strip()
    category_code = request.form.get('category_code', '').strip()
    product_name = request.form.get('product_name', '').strip()

    product_list = get_products(product_code, category_code, product_name) 
    category_list = get_category()
    return render_template('product_manage/products.html', product_list = product_list, category_list = category_list,
                           product_code = product_code, category_code = category_code, product_name = product_name)

@app.route('/add_product', methods=['GET', 'POST'])
@app.route('/product_detail/<string:product_code>', methods=['GET', 'POST'])
def product_detail(product_code = None):
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    category_list = get_category()
    if request.method == 'POST' :   
      category_code = request.form.get('category_code')
      product_name = request.form.get('product_name')
      price_a = request.form.get('price_a') or 0.00  
      qty_break_a = request.form.get('qty_break_a')
      qty_break_a = int(qty_break_a) if qty_break_a else 0
      price_b = request.form.get('price_b') or 0.00
      qty_break_b = request.form.get('qty_break_b')
      qty_break_b = int(qty_break_b) if qty_break_b else 0
      price_c = request.form.get('price_c') or 0.00
      qty_break_c = request.form.get('qty_break_c')
      qty_break_c = int(qty_break_c) if qty_break_c else 0
      min_hire = request.form.get('min_hire') or 0
      max_hire = request.form.get('max_hire') or 0
      product_specs = request.form.get('product_specs') or ''
      product_desc = request.form.get('product_desc') or ''
      image = request.files.get('upload_image')
      success = False
      if product_code: 
            success = update_product_detail_by_code(category_code, product_name, price_a, qty_break_a,
                                          price_b, qty_break_b, price_c, qty_break_c,
                                          min_hire, max_hire, product_specs, product_desc, product_code)
            
            if success:
                  if image:
                       success = upload_product_image(product_code, image)
                       if success:
                            flash('Product updated successfully', 'success')
                       else:
                            flash('Product failed to add image', 'danger')  
                     
            else:
                  flash('Product failed to update', 'danger')  
      else:
            product_code = request.form.get('product_code')
            success = insert_product(product_code, 
            category_code, product_name, price_a, qty_break_a, price_b, qty_break_b, 
            price_c, qty_break_c, min_hire, max_hire, product_specs, product_desc)
            if success:
                  if image:
                       success = upload_product_image(product_code, image)
                       if success:
                            flash('Product added successfully', 'success')  
                       else:
                            flash('Product failed to add image', 'danger')  
                  
            else:
                  flash('Product failed to add', 'danger')  

    if product_code:
      product = get_product_by_code(product_code)
      return render_template('product_manage/product_detail.html', product = product, category_list = category_list)
    else:
      return render_template('product_manage/add_product.html', category_list=category_list)  


@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_code = request.form['product_code']
    response = delete_product_by_code(product_code)
    if response['success']:
        flash(response['message'], 'success')
    else:
        flash(response['message'], 'danger')
    return redirect(url_for('products'))



@app.route('/machines', methods=['GET', 'POST'])
def machines():
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    product_code = request.form.get('product_code', '').strip()
    sn = request.form.get('sn', '').strip()
    role = session['role'] 

    if role == 'staff' or role == 'lmgr':
          store_id = session['store_id'] 
    else:
         store_id = request.form.get('store_id', '').strip()

    machine_list =get_machines(product_code, store_id, sn)
    product_list = get_products()
    store_list = get_store()
    if request.method == 'POST':
      machine_id = request.form.get('machine_id')
      action_type = request.form.get('type')
      if action_type == 'Repair':
           result = update_machine_statusToRepair_by_id(machine_id)
           return result
      if action_type == 'Disable':
           result = update_machine_statusToDisable_by_id(machine_id)
           return result
      if action_type == 'Active':
           result = update_machine_statusToActive_by_id(machine_id)
           return result
    return render_template('product_manage/machines.html', machine_list = machine_list, product_list = product_list, store_list = store_list,
                           product_code = product_code, store_id = store_id, sn = sn)
        
@app.route('/machine_detail/<int:id>', methods=['GET', 'POST'])
def machine_detail(id):
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    active_tab = request.args.get('active_tab', 'tab1') 
    machine = get_machine_by_id(id)
    product_list = get_products()
    message = request.args.get('message')
    machine_service = get_service_record_by_id(id)
    machine_hire = get_hire_record_by_id(id)
    return render_template('product_manage/machine_detail.html', machine = machine, 
                           product_list = product_list, machine_service = machine_service, 
                           machine_hire = machine_hire, active_tab = active_tab, message = message)

@app.route('/add_service_record/<int:machine_id>', methods=['GET', 'POST'])
def add_service_record(machine_id):
      allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
      if request.method == 'POST':
            service_date = request.form['service_date']
            service_name = request.form['service_name']
            note = request.form['note']

            add_service_record(machine_id, service_date, service_name, note)

            flash('Add successfully', 'success') 
            return redirect(url_for('machine_detail', id = machine_id, active_tab = 'tab3'))
      return render_template('product_manage/add_service_record.html',machine_id = machine_id)

@app.route("/editMachine",methods=["POST","GET"])
def editMachine():
      allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
      if request.method == 'POST' :
            userid = request.form[ 'id' ]
            product = get_machine_by_id(userid)
            store = get_store()
      return jsonify({'htmlresponse': render_template('editDetail.html',product = product, store = store)})

@app.route("/submitEdit",methods=["POST","GET"])
def submitEdit():
      allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
      if request.method == 'POST' :
            id = request.form.get('id')
            sn = request.form.get('sn')
            store_id = request.form.get('store_id')
            purchase_date = request.form.get('date')
            cost = request.form.get('cost')
            specs = request.form.get('specs')
            success = update_machine_detail_by_id(id, sn, store_id, purchase_date, cost, specs)

      # Check if the update was successful
      if success:
            return redirect(f'/machine_detail/{id}?message=Machine details updated successfully')
      else:
            return redirect(f'/machine_detail/{id}?message=Failed to update machine details')

@app.route('/category', methods=['GET', 'POST'])
def category():
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    category_name = request.form.get('category_name', '').strip()
    category_list = get_category(category_name)
    return render_template('product_manage/category.html', category_list = category_list, category_name = category_name)

@app.route('/category_add', methods=['POST'])
def category_add():
    allow_role(['admin'])
    category_code = request.form['category_code'].strip()
    category_name = request.form['category_name'].strip()
    
    if not check_exist_category(category_code):
      response = add_category(category_code, category_name)  
    else:
      response = {'success': False, 'message': 'Category Code Exists'}
      return jsonify(response)  
    
    if response['success']:
        flash(response['message'], 'success')
    else:
        flash(response['message'], 'danger')
        
    return jsonify(response)

@app.route('/category_edit', methods=['POST'])
def category_edit():
    allow_role(['admin'])
    category_code = request.form['category_code'].strip()
    category_name = request.form['category_name'].strip()
    
    response = update_category(category_code, category_name)
    if response['success']:
        flash(response['message'], 'success')
    else:
        flash(response['message'], 'danger')
        
    return jsonify(response)

@app.route('/delete_category', methods=['GET', 'POST'])
def delete_category():
    allow_role(['admin'])
    category_code = request.form['category_code']
    response = delete_category(category_code)  
    if response['success']:
        flash(response['message'], 'success')
    else:
        flash(response['message'], 'danger')
    return redirect(url_for('category'))




def get_category(category_name=None):
    """
    Fetch categories with optional name filter.
    """
    params = []
    sql = "SELECT * FROM category WHERE 1=1"
    
    if category_name:
        sql += " AND name LIKE %s"
        params.append(f"%{category_name}%")
    
    sql += " ORDER BY name"
    
    cursor = db.get_cursor()
    cursor.execute(sql, params)
    return cursor.fetchall()


def check_exist_category(category_code):
    """
    Returns True if category_code already exists.
    """
    sql = "SELECT COUNT(*) AS num FROM category WHERE category_code = %s"
    cursor = db.get_cursor()
    cursor.execute(sql, (category_code,))
    count = cursor.fetchone()["num"]
    return count > 0


def add_category(category_code, category_name):
    """
    Adds a new category.
    """
    try:
        sql = "INSERT INTO category (category_code, name) VALUES (%s, %s)"
        cursor = db.get_cursor()
        cursor.execute(sql, (category_code, category_name))
        db.connection.commit()
        return {"success": True, "message": "Category added successfully"}
    except Exception as err:
        db.connection.rollback()
        return {"success": False, "message": f"Error adding category: {err}"}


def update_category(category_code, category_name):
    """
    Updates an existing category.
    """
    try:
        sql = "UPDATE category SET name = %s WHERE category_code = %s"
        cursor = db.get_cursor()
        cursor.execute(sql, (category_name, category_code))
        db.connection.commit()
        return {"success": True, "message": "Category updated successfully"}
    except Exception as err:
        db.connection.rollback()
        return {"success": False, "message": f"Error updating category: {err}"}


def delete_category(category_code):
    """
    Deletes a category by code.
    """
    try:
        sql = "DELETE FROM category WHERE category_code = %s"
        cursor = db.get_cursor()
        cursor.execute(sql, (category_code,))
        db.connection.commit()
        return {"success": True, "message": "Category deleted successfully"}
    except Exception as err:
        db.connection.rollback()
        if "FOREIGN KEY" in str(err):
            return {"success": False, "message": "This category is in use and cannot be deleted!"}
        return {"success": False, "message": f"Error deleting category: {err}"}


def get_products(product_code = None, category_code = None, product_name = None):
      params = []
      sql = '''SELECT p.*,c.`name` AS category_name FROM product p 
            INNER JOIN category c ON p.category_code=c.category_code Where 1=1'''
      if product_code:
            sql += ' AND p.product_code LIKE %s'
            params.append(f'%{product_code}%')
      if category_code:
            sql += ' AND p.category_code = %s'
            params.append(category_code)
      if product_name:
            sql += ' AND p.name LIKE %s'
            params.append(f'%{product_name}%')
      
      sql += ' ORDER BY category_name;'
      cursor = db.get_cursor()
      cursor.execute(sql, params)       
      return cursor.fetchall() 

def get_machines(product_code = None, store_id  = None, sn = None):
      params = []
      sql = '''SELECT m.*,s.store_name AS store_name,p.`name` AS product_name  FROM machine m
            INNER JOIN store s ON m.store_id=s.store_id
            INNER JOIN product p ON m.product_code=p.product_code WHERE 1=1'''
      if product_code:
            sql += ' AND m.product_code = %s'
            params.append(product_code)
      if store_id: 
            sql += ' AND m.store_id = %s'
            params.append(store_id)
      if sn: 
            sql += ' AND m.sn LIKE %s'
            params.append(f'%{sn}%')
      sql += ' ORDER BY m.sn;'     
      cursor = db.get_cursor()   
      cursor.execute(sql, params)  
      return cursor.fetchall() 
 
def get_machine_by_id(machine_id):
      sql = '''SELECT m.*,s.store_name AS store_name,p.`name` AS product_name, p.specs AS specs  FROM machine m
            INNER JOIN store s ON m.store_id=s.store_id
            INNER JOIN product p ON m.product_code=p.product_code WHERE machine_id = %s;''' 
      cursor = db.get_cursor()     
      cursor.execute(sql,(machine_id,))  
      return cursor.fetchone() 

def get_product_by_code(product_code):
      sql = '''SELECT p.*,c.`name` AS category_name  FROM `product` p
                  INNER JOIN category c ON p.category_code = c.category_code
                  WHERE p.product_code = %s;'''
      cursor = db.get_cursor()     
      cursor.execute(sql,(product_code,))  
      return cursor.fetchone() 

def get_store():
     sql = 'SELECT * FROM store;' 
     cursor = db.get_cursor()     
     cursor.execute(sql)  
     return cursor.fetchall() 

def update_machine_statusToRepair_by_id(id):
      sql = 'UPDATE machine SET status = 0 WHERE machine_id = %s;' 
      cursor = db.get_cursor()     
      cursor.execute(sql,(id,))  
      if cursor.rowcount == 1:
        return jsonify({'success': True,})
      else:
        return jsonify({'success': False, 'error': 'Something went wrong'}), 500 
      
def update_machine_statusToDisable_by_id(id):
      sql = 'UPDATE machine SET status = -1 WHERE machine_id = %s;' 
      cursor = db.get_cursor()     
      cursor.execute(sql,(id,))  
      if cursor.rowcount == 1:
        return jsonify({'success': True,})
      else:
        return jsonify({'success': False, 'error': 'Something went wrong'}), 500 
      
def update_machine_statusToActive_by_id(id):
      sql = 'UPDATE machine SET status = 1 WHERE machine_id = %s;' 
      cursor = db.get_cursor()     
      cursor.execute(sql,(id,))  
      if cursor.rowcount == 1:
        return jsonify({'success': True,})
      else:
        return jsonify({'success': False, 'error': 'Something went wrong'}), 500 
      
def update_machine_detail_by_id(id, sn, store_id, purchase_date, cost, specs):
      machine_update_sql = '''
        UPDATE machine 
        SET sn = %s, purchase_date = %s, cost = %s, store_id = %s
        WHERE machine_id = %s;'''
    
      cursor = db.get_cursor()   
       # Update machine table
      cursor.execute(machine_update_sql, (sn, purchase_date, cost, store_id, id))
      machine_updated = cursor.rowcount
      if machine_updated == 1:
            return True
      else:
            return False

def get_service_record_by_id(machine_id):
      sql = 'SELECT * FROM service WHERE machine_id = %s ORDER BY service_date DESC;'  
      cursor = db.get_cursor()   
      cursor.execute(sql, (machine_id,))  
      return cursor.fetchall()

# def get_hire_record_by_id(machine_id):
#       sql = '''SELECT hr.*,CONCAT(s1.first_name, ' ', s1.last_name) checkout_staff_full_name,CONCAT(s2.first_name, ' ',
#                   s2.last_name) AS return_staff_full_name, bi.machine_id
#                   FROM hire_record hr
#                   INNER JOIN staff s1 ON hr.checkout_staff = s1.staff_id
#                   INNER JOIN staff s2 ON hr.return_staff = s2.staff_id
#                   INNER JOIN booking_item bi ON hr.booking_item_id =bi.booking_item_id
#                   WHERE bi.machine_id = %s
#                   ORDER BY hr.checkout_time DESC;'''
#       cursor = db.get_cursor()
#       cursor.execute(sql, (machine_id,))
#       return cursor.fetchall()


# def get_hire_record_by_id(machine_id):
#     sql = '''SELECT hr.*, 
#                     CONCAT(s1.first_name, ' ', s1.last_name) AS checkout_staff_full_name,
#                     CONCAT(s2.first_name, ' ', s2.last_name) AS return_staff_full_name, 
#                     bi.machine_id
#              FROM hire_record hr
#              INNER JOIN staff s1 ON hr.checkout_staff = s1.staff_id
#              LEFT JOIN staff s2 ON hr.return_staff = s2.staff_id  -- ✅ FIX
#              INNER JOIN booking_item bi ON hr.booking_item_id = bi.booking_item_id
#              WHERE bi.machine_id = %s
#              ORDER BY hr.checkout_time DESC;'''
#     cursor = db.get_cursor()
#     cursor.execute(sql, (machine_id,))
#     return cursor.fetchall()


def get_hire_record_by_id(machine_id):
    sql = '''SELECT hr.*, 
                    CONCAT(s1.first_name, ' ', s1.last_name) AS checkout_staff_full_name,
                    CONCAT(s2.first_name, ' ', s2.last_name) AS return_staff_full_name, 
                    bi.machine_id
             FROM hire_record hr
             INNER JOIN staff s1 ON hr.checkout_staff = s1.staff_id
             LEFT JOIN staff s2 ON hr.return_staff = s2.staff_id   -- ✅ LEFT JOIN fix
             INNER JOIN booking_item bi ON hr.booking_item_id = bi.booking_item_id
             WHERE bi.machine_id = %s
             ORDER BY hr.checkout_time DESC;'''
    cursor = db.get_cursor()
    cursor.execute(sql, (machine_id,))
    return cursor.fetchall()



def add_service_record(machine_id, service_date, service_name, note):
      sql = '''INSERT INTO service (machine_id, service_date, service_name, note) 
            VALUES (%s, %s, %s, %s);'''
      cursor = db.get_cursor()
      cursor.execute(sql, (machine_id, service_date, service_name, note))
      return cursor.fetchone()

def update_product_detail_by_code(category_code, product_name, price_a, qty_break_a,
                                               price_b, qty_break_b, price_c, qty_break_c,
                                               min_hire, max_hire, product_specs, product_desc, 
                                               product_code):
      product_update_sql = '''
            UPDATE product 
            SET 
                  category_code = %s,
                  `name`  = %s,
                  price_a = %s,
                  qty_break_a = %s,
                  price_b = %s,
                  qty_break_b = %s,
                  price_c = %s,
                  qty_break_c = %s,
                  min_hire = %s,
                  max_hire = %s,
                  specs = %s,
                  `desc` = %s,
                  status = 1
            WHERE 
                  product_code = %s;
            '''
      cursor = db.get_cursor()   
      try:
            cursor.execute(product_update_sql, (
            category_code, product_name, price_a, qty_break_a, price_b, qty_break_b, 
            price_c, qty_break_c, min_hire, max_hire, product_specs, product_desc, product_code
            ))
            db.connection.commit()  
            return True
      except Exception as err:
            return False

def insert_product(product_code, 
            category_code, product_name, price_a, qty_break_a, price_b, qty_break_b, 
            price_c, qty_break_c, min_hire, max_hire, product_specs, product_desc):
    product_insert_sql = '''
            INSERT INTO product (
                  product_code,
                  category_code,
                  `name`,
                  price_a,
                  qty_break_a,
                  price_b,
                  qty_break_b,
                  price_c,
                  qty_break_c,
                  min_hire,
                  max_hire,
                  specs,
                  `desc`,
                  status) 
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1);'''
    cursor = db.get_cursor()
    try:
        
        cursor.execute(product_insert_sql, (product_code, 
            category_code, product_name, price_a, qty_break_a, price_b, qty_break_b, 
            price_c, qty_break_c, min_hire, max_hire, product_specs, product_desc
        ))
        db.connection.commit()
        return True
    except Exception as err:
        return False

def delete_product_by_code(product_code):
    """
    Deletes a product by its code.
    """
    try:
        sql = "DELETE FROM product WHERE product_code = %s"
        cursor = db.get_cursor()
        cursor.execute(sql, (product_code,))
        db.connection.commit()   # ✅ Commit after delete
        return {"success": True, "message": "Product deleted successfully"}
    except Exception as err:
        db.connection.rollback()  # ✅ Rollback if error
        if "FOREIGN KEY" in str(err):
            return {"success": False, "message": "This product is in use and cannot be deleted!"}
        return {"success": False, "message": f"Error deleting product: {err}"}
  
  
  
  
  
  
@app.route('/machines/delete', methods=['POST'])
def delete_machine():
    allow_role(['nmgr', 'admin'])   # Only higher roles can delete
    machine_id = request.form.get('machine_id')

    try:
        sql = "DELETE FROM machine WHERE machine_id = %s"
        cursor = db.get_cursor()
        cursor.execute(sql, (machine_id,))
        db.connection.commit()

        return jsonify({"success": True, "message": "Machine deleted successfully"})
    except Exception as err:
        db.connection.rollback()
        if "FOREIGN KEY" in str(err):
            return jsonify({"success": False, "message": "This machine is linked with other records and cannot be deleted!"})
        return jsonify({"success": False, "message": f"Error deleting machine: {err}"})
