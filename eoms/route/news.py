# Old Error 'TypeError: 'NoneType' object is not subscriptable' in admin only when click on News. 
# # New Code to solve error "TypeError: 'NoneType' object is not subscriptable"
from eoms import app
from flask import render_template, redirect, request, flash, url_for, session, jsonify
from eoms.model import db
from datetime import datetime
from eoms.route import promotion
from eoms.model.session_utils import allow_role
import mysql.connector

@app.route('/view_news_list', methods=['GET', 'POST'])
def view_news_list():
    news_list = get_news_list()
    return render_template('customer/view_news_list.html', news_list=news_list)

@app.route('/customer_view_news_detail/<int:news_id>', methods=['GET', 'POST'])
def customer_view_news_detail(news_id):
    sql = '''SELECT n.*, s.store_id, s.store_name 
             FROM news n
             INNER JOIN store s ON n.store_id = s.store_id
             WHERE news_id = %s;'''
    cursor = db.get_cursor()
    cursor.execute(sql, (news_id,))
    news_details = cursor.fetchone()
    return render_template('customer/news_page.html', news_details=news_details)

def get_news_list():
    sql = '''SELECT n.*, s.store_id, s.store_name 
             FROM news n
             INNER JOIN store s ON n.store_id = s.store_id 
             ORDER BY create_date DESC;'''
    cursor = db.get_cursor()
    cursor.execute(sql)
    return cursor.fetchall()

@app.route('/manage_news', methods=['GET', 'POST'])
def manage_news():
    show_news_list = []
    store_id = []
    allow_role(['lmgr', 'nmgr', 'admin'])

    news_title = request.form.get('news_title', '').strip()
    store_list = promotion.get_store_list()
    role = session['role']

    if role == 'lmgr':
        store_id = session['store_id']
    elif role in ['nmgr', 'admin']:
        store_id = request.form.get('store_id', '').strip()

    if not news_title and not store_id:
        news_list = get_news_list()
    else:
        news_list = get_news(news_title, store_id)

    for n in news_list:
        news_id = n['news_id']
        news_title = n['title']
        news_content = n['content']
        news_create_date = n['create_date']
        news_status = n['status']
        n_store_id = n['store_id']

        store_data = promotion.get_store_name(n_store_id)
        if store_data and 'store_name' in store_data:
            store_name = store_data['store_name']
        else:
            store_name = 'Unknown Store'

        n_list = {
            'news_id': news_id,
            'store_name': store_name,
            'title': news_title,
            'content': news_content,
            'create_date': news_create_date,
            'status': news_status
        }
        show_news_list.append(n_list)

    return render_template('dashboard/manage_news.html', show_news_list=show_news_list, store_list=store_list)

def get_news(news_title=None, store_id=None):
    sql = "SELECT * FROM news WHERE 1=1"
    params = []

    if news_title:
        sql += " AND title LIKE %s"
        params.append(f"%{news_title}%")

    if store_id:
        sql += " AND store_id = %s"
        params.append(store_id)

    sql += " ORDER BY create_date DESC;"
    cursor = db.get_cursor()
    cursor.execute(sql, params)
    return cursor.fetchall()

def get_news_by_news_id(news_id):
    sql = 'SELECT * FROM news WHERE news_id = %s;'
    cursor = db.get_cursor()
    cursor.execute(sql, (news_id,))
    return cursor.fetchone()

@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    role = session['role']
    store_id = []
    store_list = promotion.get_store_list()

    if request.method == 'POST':
        news_title = request.form.get('news_title')
        news_content = request.form.get('news_content')

        if role == 'lmgr':
            store_id = session['store_id']
        elif role in ['nmgr', 'admin']:
            store_id = request.form.get('store_id', '').strip()

        success = insert_news(store_id, news_title, news_content)
        if success:
            flash('News added successfully', 'success')
        else:
            flash('News failed to add', 'danger')

    return render_template('dashboard/add_news.html', store_list=store_list)

@app.route('/update_news_detail/<string:news_id>', methods=['GET', 'POST'])
def update_news_detail(news_id):
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    role = session['role']
    store_list = promotion.get_store_list()

    if request.method == 'POST':
        news_title = request.form.get('news_title')
        news_content = request.form.get('news_content')

        if role == 'lmgr':
            store_id = session['store_id']
        elif role in ['nmgr', 'admin']:
            store_id = request.form.get('store_id', '').strip()

        success = update_news_detail_by_news_id(news_id, store_id, news_title, news_content)
        if success:
            flash('News updated successfully', 'success')
        else:
            flash('News failed to update', 'danger')

    news = get_news_by_news_id(news_id)
    return render_template('dashboard/news_details.html', news=news, store_list=store_list)

def insert_news(store_id, title, content):
    cursor = db.get_cursor()
    cursor.execute(
        'INSERT INTO news (store_id, title, content, create_date, status) VALUES (%s, %s, %s, %s, 1);',
        (store_id, title, content, datetime.now())
    )
    db.connection.commit()
    return True

def update_news_detail_by_news_id(news_id, store_id, news_title, news_content):
    cursor = db.get_cursor()
    try:
        cursor.execute(
            'UPDATE news SET store_id = %s, title = %s, content = %s, create_date = %s WHERE news_id = %s;',
            (store_id, news_title, news_content, datetime.now(), news_id)
        )
        db.connection.commit()
        return True
    except mysql.connector.errors.Error:
        return False

@app.route('/delete_news/<int:news_id>', methods=['GET', 'POST'])
def delete_news(news_id):
    allow_role(['lmgr', 'nmgr', 'admin'])
    cursor = db.get_cursor()
    cursor.execute("DELETE FROM news WHERE news_id = %s;", (news_id,))
    db.connection.commit()
    flash('Delete successfully', 'success')
    return redirect(url_for('manage_news'))





# Old Error 'TypeError: 'NoneType' object is not subscriptable' in admin only when click on News. 
# from eoms import app
# from flask import render_template, redirect, request, flash, url_for,session,jsonify
# from eoms.model import db
# from datetime import datetime
# from eoms.route import promotion
# from eoms.model.session_utils import allow_role
# import mysql.connector
# from eoms.model.datetime_utils import datetime_to_nz




# @app.route('/view_news_list', methods=['GET', 'POST'])
# def view_news_list():
#     news_list = get_news_list()
#     return render_template('customer/view_news_list.html', news_list=news_list)


# @app.route('/customer_view_news_detail/<int:news_id>', methods=['GET', 'POST'])
# def customer_view_news_detail(news_id):
#     sql = '''SELECT n.* ,s.store_id, s.store_name FROM news n
#                  INNER JOIN store s ON  n.store_id = s.store_id
#                  WHERE news_id = %s;'''
#     connection = db.get_cursor()
#     connection.execute(sql,(news_id,))
#     news_details = connection.fetchone()
#     return render_template('customer/news_page.html', news_details=news_details)



# def get_news_list():
#     # allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
#     sql = '''SELECT n.* ,s.store_id, s.store_name FROM news n
#              INNER JOIN store s ON  n.store_id = s.store_id 
#              ORDER BY create_date DESC;'''
#     connection = db.get_cursor()
#     connection.execute(sql)
#     return connection.fetchall()


# @app.route('/manage_news', methods=['GET', 'POST'])
# def manage_news():
#     show_news_list = []
#     store_id =[]
#     allow_role(['lmgr', 'nmgr', 'admin'])
#     news_title = request.form.get('news_title', '').strip()
#     store_list = promotion.get_store_list()
#     role = session['role']

#     if role == 'lmgr':
#         store_id = session['store_id']

#     elif role == 'nmgr' or role == 'admin':
#         store_id = request.form.get('store_id', '').strip()
#     print(store_id)
#     if news_title is None and store_id is None:
#         news_list = get_news_list()
#     else:
#         news_list = get_news(news_title, store_id)
#     for n in news_list:
#         print(n)

#     for n in news_list:
#         news_id = n['news_id']
#         news_title = n['title']
#         news_content = n['content']
#         news_create_date = n['create_date']
#         news_status = n['status']
#         n_store_id = n['store_id']
#         store_name = promotion.get_store_name(n_store_id)['store_name']

#         #check user, local manager only manage their own store news
#         n_list = {
#             'news_id': news_id,
#             'store_name': store_name,
#             'title': news_title,
#             'content': news_content,
#             'create_date': news_create_date,
#             'status': news_status
#                 }
#         show_news_list.append(n_list)
#     for p in show_news_list:
#         print(p)
#     return render_template('dashboard/manage_news.html', show_news_list=show_news_list, store_list=store_list)


# def get_news(new_title=None, store_id=None):
#     params = []
#     sql = '''SELECT * FROM news '''
#     if new_title:
#         sql += ' AND title LIKE %s'
#         params.append(f'%{new_title}%')
#     if store_id:
#         sql += ' WHERE store_id = %s'
#         params.append(store_id)
#     sql += ' ORDER BY create_date DESC;'
#     cursor = db.get_cursor()
#     cursor.execute(sql, params)
#     return cursor.fetchall()
# def get_news_by_news_id(news_id):
#     sql = 'SELECT * FROM news WHERE news_id = %s; '
#     cursor = db.get_cursor()
#     cursor.execute(sql, (news_id,))
#     return cursor.fetchone()

# # @app.route("/news/detail/<int:news_id>", methods=['GET', 'POST'])
# # def news_detail(news_id):
# #     cursor = db.get_cursor()
# #     cursor.execute('SELECT * FROM news WHERE news_id=%s;', (news_id,))
# #     news = cursor.fetchone()
# #
# #     return render_template('dashboard/news_details.html', news=news)
# @app.route('/add_news', methods=['GET', 'POST'])
# def add_news():
#     allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
#     role = session['role']
#     store_id = []
#     store_list = promotion.get_store_list()
#     if request.method == 'POST':
#         news_title = request.form.get('news_title')
#         if role == 'lmgr':
#             store_id = session['store_id']
#         elif role == 'nmgr' or role == 'admin':
#             store_id = request.form.get('store_id', '').strip()
#             print(store_id)
#         news_content = request.form.get('news_content')
#         print(news_title,store_id,news_content)
#         success = insert_news(store_id, news_title, news_content)
#         if success:
#             flash('News added successfully', 'success')
#         else:
#             flash('News failed to add', 'danger')
#     return render_template('dashboard/add_news.html', store_list=store_list)

# @app.route('/update_news_detail/<string:news_id>', methods=['GET', 'POST'])
# def update_news_detail(news_id):
#     allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
#     role = session['role']
#     store_id = []
#     store_list = promotion.get_store_list()
#     if request.method == 'POST':
#         news_title = request.form.get('news_title')
#         if role == 'lmgr':
#             store_id = session['store_id']
#         elif role == 'nmgr' or role == 'admin':
#             store_id = request.form.get('store_id', '').strip()
#             print(store_id)
#         news_content = request.form.get('news_content')
#         print(news_title,store_id,news_content)
#         success = False
#         success =  update_news_detail_by_news_id(news_id, store_id, news_title, news_content)
#         if success:
#             flash('News updated successfully', 'success')
#         else:
#             flash('News failed to update', 'danger')

#             print(success)

#     news = get_news_by_news_id(news_id)
#     print(promotion)
#     return render_template('dashboard/news_details.html', news=news, store_list=store_list)


# def insert_news(store_id, title, content):
#     cursor = db.get_cursor()
#     cursor.execute('INSERT INTO news (store_id, title, content, create_date,status) VALUES (%s, %s, %s, %s,1);',
#                    (store_id, title, content, datetime.now()))
#     db.connection.commit()
#     return True

# def update_news_detail_by_news_id(news_id,store_id,news_title,news_content):
#     print(news_id,news_title,store_id,news_content)
#     cursor = db.get_cursor()
#     try:
#         cursor.execute('UPDATE news SET store_id = %s,title=%s, content=%s, create_date= %s WHERE news_id=%s;', (store_id,news_title, news_content, datetime.now(),news_id))
#         db.connection.commit()
#         return True
#     except mysql.connector.errors as err:
#         return False

# @app.route('/delete_news/<int:news_id>', methods=['GET', 'POST'])
# def delete_news(news_id):
#     allow_role(['lmgr', 'nmgr', 'admin'])
#     cursor = db.get_cursor()
#     cursor.execute("DELETE FROM news WHERE news_id = %s;", (news_id,))
#     db.connection.commit()
#     flash('Delete successfully', 'success')
#     return redirect(url_for('manage_news'))