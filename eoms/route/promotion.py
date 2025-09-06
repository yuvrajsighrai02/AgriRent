from eoms import app
from flask import render_template, redirect, request, flash, url_for,session,jsonify, abort
from eoms.model import db
from datetime import datetime, timedelta
from eoms.model.session_utils import allow_role
# We are replacing get_all_current_promo, so this import is no longer needed for this function
from eoms.model.promotion import get_products_by_promo_code 
from eoms.route import inventory

# Promotion list
@app.route('/promotion')
def view_promotion():
    """
    This function now directly queries the database for active promotions.
    It selects promotions that have status = 1 (active) and have not expired.
    """
    sql = """
        SELECT * FROM promotion 
        WHERE status = 1 AND end_date >= CURDATE()
        GROUP BY promo_code;
    """
    cursor = db.get_cursor()
    cursor.execute(sql)
    promotion_list = cursor.fetchall()
    return render_template('shopping/promotion_list.html', promotion_list=promotion_list)

# Promition product list
@app.route('/promotion/<promo_code>')
def view_promotion_products(promo_code):
    promo = get_promotion_by_id(promo_code)
    # Check if promotion is valid
    # THE FIX IS ON THIS LINE: We add .date() to promo.get('end_date')
    if promo and promo.get('status') == 1 and promo.get('end_date').date() >= datetime.now().date():
        equipment_list = get_products_by_promo_code(promo_code)
        current_category = {'name': promo.get('name') or promo['promo_code']}
        return render_template('/shopping/equipment_list.html', equipment_list=equipment_list, current_category=current_category)
    else:
        abort(404)

# --- The rest of your file remains the same ---

def get_all_promotion():
    sql = '''SELECT p.*, pp.product_code FROM promotion p
              INNER JOIN promo_product pp ON  p.promo_code = pp.promo_code; '''
    cursor = db.get_cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def get_promotion_by_id(promo_code):
    sql = 'SELECT * FROM promotion WHERE promo_code = %s; '
    cursor = db.get_cursor()
    cursor.execute(sql,(promo_code,))
    return cursor.fetchone()


def get_promotion_and_product_by_id(promo_code):
    sql = '''SELECT p.*, pp.* FROM promotion p 
            INNER JOIN promo_product pp ON p.promo_code = pp.promo_code
            WHERE p.promo_code = %s; '''
    cursor = db.get_cursor()
    cursor.execute(sql, (promo_code,))
    return cursor.fetchone()

def get_store_name(store_id):
    sql = 'SELECT store_name, store_id FROM store WHERE store_id = %s; '
    cursor = db.get_cursor()
    cursor.execute(sql, (store_id,))
    return cursor.fetchone()


def get_store_list():
    sql = 'SELECT store_name, store_id FROM store; '
    cursor = db.get_cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def get_product_code_list():
    sql = 'SELECT product_code FROM product; '
    cursor = db.get_cursor()
    cursor.execute(sql)
    return cursor.fetchall()
def get_all_promotion_store():
    promotion_store_list = []
    promotion = get_all_promotion()
    for p in promotion:
        store_id = p['store_id']
        store_name = get_store_name(store_id)['store_name']
        if store_name not in promotion_store_list:
            promotion_store_list.append(store_name)
    return promotion_store_list


def get_product_code(product_code):
    sql = 'SELECT * FROM product WHERE product_code = %s; '
    cursor = db.get_cursor()
    cursor.execute(sql, (product_code,))
    return cursor.fetchone()


@app.route('/manage_promotion', methods=['GET', 'POST'])
def manage_promotion():
    store_id = []
    allow_role(['lmgr', 'nmgr', 'admin'])
    product_code = request.form.get('product_code', '').strip()
    category_code = request.form.get('category_code', '').strip()
    product_name = request.form.get('product_name', '').strip()
    category_list = inventory.get_category()
    store_list = get_store_list()

    role = session['role']

    if role == 'lmgr':
        store_id = session['store_id']
    elif role == 'nmgr' or role == 'admin':
        store_id = request.form.get('store_id', '').strip()

    promotion_list = get_promotions(product_code, category_code, product_name, store_id)

    for p in promotion_list:
        print(p)

    return render_template('staff_product/manage_promotion.html', category_list=category_list,
                           promotion_list=promotion_list, store_list=store_list)


def get_promotions(product_code=None, category_code=None, product_name=None, store_id=None):
    params = []
    sql = '''select p.*, pp.product_code, pr.name AS product_name,pr.category_code,pr.price_a,c.name AS category_name from promotion p
            INNER JOIN promo_product pp on p.promo_code = pp.promo_code
            INNER JOIN product pr on pr.product_code = pp.product_code
            INNER JOIN category c on c.category_code = pr.category_code'''
    if product_code:
        sql += ' AND pp.product_code LIKE %s'
        params.append(f'%{product_code}%')
    if category_code:
        sql += ' AND pr.category_code = %s'
        params.append(category_code)
    if product_name:
        sql += ' AND pr.name LIKE %s'
        params.append(f'%{product_name}%')
    if store_id:
        sql += ' AND p.store_id = %s'
        params.append(store_id)

    sql += ' ;'
    cursor = db.get_cursor()
    cursor.execute(sql, params)
    return cursor.fetchall()

@app.route('/add_promotion', methods=['GET', 'POST'])
def add_promotion(promo_code = None):
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    role = session['role']
    store_id = []
    store_list = get_store_list()
    product_code_list= get_product_code_list()
    if request.method == 'POST':
        promo_code = request.form.get('promo_code')
        product_code = request.form.get('product_code')
        if role == 'lmgr':
            store_id = session['store_id']
        elif role == 'nmgr' or role == 'admin':
            store_id = request.form.get('store_id', '').strip()
            print(store_id)
        promo_start_date = request.form.get('promo_start_date')
        promo_end_date = request.form.get('promo_end_date')
        promo_rate = request.form.get('promo_rate')
        promo_desc = request.form.get('promotion_desc')
        print(promo_code, product_code, store_id, promo_start_date, promo_rate,  promo_desc, promo_end_date)
        product_code = request.form.get('product_code')
        success = insert_promotion(promo_code, product_code, store_id, promo_rate, promo_start_date, promo_end_date, promo_desc)
        if success:
            flash('Promotion added successfully', 'success')
        else:
            flash('Promotion failed to add', 'danger')
    return render_template('staff_product/add_promotion.html', store_list=store_list, product_code_list= product_code_list)


@app.route('/update_promotion_detail/<string:promo_code>', methods=['GET', 'POST'])
def update_promotion_detail(promo_code=None):
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    role = session['role']
    store_id = []
    store_list = get_store_list()
    if request.method == 'POST':
        promo_code = request.form.get('promo_code')
        product_code = request.form.get('product_code')
        if role == 'lmgr':
            store_id = session['store_id']
        elif role == 'nmgr' or role == 'admin':
            store_id = request.form.get('store_id', '').strip()
            print(store_id)
        promo_start_date = request.form.get('promo_start_date')
        promo_end_date = request.form.get('promo_end_date')
        promotion_rate = request.form.get('promo_rate')
        promo_desc = request.form.get('promotion_desc')
        success = False
        success = update_promotion_detail_by_code(product_code, promo_code, store_id, promotion_rate,
                                                  promo_start_date, promo_end_date, promo_desc)
        if success:
            flash('Promotion updated successfully', 'success')
        else:
            flash('Promotion failed to update', 'danger')

        print(success)

    promotion = get_promotion_and_product_by_id(promo_code)
    print(promotion)
    return render_template('staff_product/promotion_details.html', promotion=promotion, store_list=store_list)



def insert_promotion(promo_code, product_code, store_id, disc_rate, start_date, end_date, desc):

    query = """INSERT INTO promotion (promo_code, store_id, disc_rate, start_date, end_date, `desc`, status)
                VALUES (%(promo_code)s, %(store_id)s, %(disc_rate)s, %(start_date)s,
                %(end_date)s, %(desc)s,1);
            """
    cursor = db.get_cursor()
    cursor.execute(
        query,
        {
            "promo_code": promo_code,
            "store_id": store_id,
            "disc_rate": disc_rate,
            "start_date": start_date,
            "end_date": end_date,
            "desc": desc,
        }
    )
    sql = 'INSERT INTO promo_product (promo_code, product_code) VALUES (%s, %s);'
    cursor = db.get_cursor()
    cursor.execute(sql, (promo_code, product_code))
    db.connection.commit()
    return True


def update_promotion_detail_by_code(product_code, promo_code, store_id, promotion_rate,
                                    promo_start_date, promo_end_date,  promo_desc):
    print(product_code, promo_code, store_id, promotion_rate, promo_start_date, promo_end_date,  promo_desc)
    cursor = db.get_cursor()
    promotion_update_sql = '''
            UPDATE promotion 
            SET 
                  store_id = %s,
                  disc_rate = %s,
                  start_date = %s,
                  end_date = %s,
                  `desc` = %s,
                  status = 1
            WHERE 
                  promo_code = %s;
            '''
    cursor.execute(promotion_update_sql, (
                store_id, promotion_rate,
                promo_start_date, promo_end_date, promo_desc, promo_code
            ))
    db.connection.commit()
    return True

@app.route('/delete_promotion/<promo_code>/<product_code>', methods=['GET', 'POST'])
def delete_promotion(promo_code , product_code):
    allow_role(['lmgr', 'nmgr', 'admin'])
    cursor = db.get_cursor()
    cursor.execute("DELETE FROM promo_product WHERE promo_code = %s AND product_code = %s;", (promo_code, product_code,))
    db.connection.commit()
    flash('Delete successfully', 'success')
    return redirect(url_for('manage_promotion'))