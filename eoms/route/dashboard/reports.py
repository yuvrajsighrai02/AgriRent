from eoms import app
from flask import render_template, jsonify, session
from eoms.model.db import get_cursor
from eoms.model.db import get_connection
from eoms.model.session_utils import allow_role

# Financial Report / Hire Status / Maintenance Records
@app.route('/financial_hire_damage_reports')
def financial_hire_damage_reports():
    allow_role(['lmgr', 'nmgr', 'admin'])
    return render_template('dashboard/financial_hire_damage_reports.html')


@app.route('/api/financial_report')
def financial_report():
    role = session.get('role', 'guest')
    store_id = session.get('store_id', None)

    with get_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            if role in ['admin', 'nmgr']:
                query = """
                    SELECT DATE_FORMAT(create_date, '%Y-%m') as month, SUM(total) as total_revenue
                    FROM booking
                    GROUP BY DATE_FORMAT(create_date, '%Y-%m')
                """
            elif role in ['staff', 'lmgr'] and store_id is not None:
                query = """
                    SELECT DATE_FORMAT(create_date, '%Y-%m') as month, SUM(total) as total_revenue
                    FROM booking
                    WHERE store_id = %s
                    GROUP BY DATE_FORMAT(create_date, '%Y-%m')
                """
            else:
                return jsonify([])

            if role in ['staff', 'lmgr']:
                cursor.execute(query, (store_id,))
            else:
                cursor.execute(query)
            result = cursor.fetchall()
    return jsonify(result)



@app.route('/api/hire_status')
def hire_status():
    role = session.get('role', 'guest')
    store_id = session.get('store_id', None)

    with get_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            if role in ['admin', 'nmgr']:
                query = """
                    SELECT DATE_FORMAT(hire_from, '%Y-%m') as month, COUNT(*) as number_of_hires
                    FROM booking_item
                    GROUP BY DATE_FORMAT(hire_from, '%Y-%m')
                """
            elif role in ['staff', 'lmgr'] and store_id is not None:
                query = """
                    SELECT DATE_FORMAT(hire_from, '%Y-%m') as month, COUNT(*) as number_of_hires
                    FROM booking_item
                    JOIN booking ON booking.booking_id = booking_item.booking_id
                    WHERE booking.store_id = %s
                    GROUP BY DATE_FORMAT(hire_from, '%Y-%m')
                """
            else:
                return jsonify([])

            if role in ['staff', 'lmgr']:
                cursor.execute(query, (store_id,))
            else:
                cursor.execute(query)
            result = cursor.fetchall()
    return jsonify(result)


@app.route('/api/maintenance_records')
def maintenance_records():
    role = session.get('role', 'guest')
    store_id = session.get('store_id', None)

    with get_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            if role in ['admin', 'nmgr']:
                query = """
                    SELECT DATE_FORMAT(service_date, '%Y-%m') as month, COUNT(*) as number_of_services
                    FROM service
                    JOIN machine ON service.machine_id = machine.machine_id
                    GROUP BY DATE_FORMAT(service_date, '%Y-%m')
                """
            elif role in ['staff', 'lmgr'] and store_id is not None:
                query = """
                    SELECT DATE_FORMAT(service_date, '%Y-%m') as month, COUNT(*) as number_of_services
                    FROM service
                    JOIN machine ON service.machine_id = machine.machine_id
                    WHERE machine.store_id = %s
                    GROUP BY DATE_FORMAT(service_date, '%Y-%m')
                """
            else:
                return jsonify([])

            if role in ['staff', 'lmgr']:
                cursor.execute(query, (store_id,))
            else:
                cursor.execute(query)
            result = cursor.fetchall()
    return jsonify(result)


# Stock Report / Customer Order /Store Report
@app.route('/stock_order_store_reports')
def stock_order_store_reports():
    allow_role(['lmgr', 'nmgr', 'admin'])
    user_role = session.get('role', 'guest')  # Defaults to 'guest' if no role information is found

    return render_template('dashboard/stock_order_store_reports.html', user_role=user_role)


@app.route('/api/product_inventory')
def product_inventory():
    role = session.get('role', 'guest')
    store_id = session.get('store_id', None)

    with get_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            if role in ['admin', 'nmgr']:
                query = """
                    SELECT c.name AS category_name, p.name AS product_name, 
                           COUNT(DISTINCT p.product_code) AS product_count, 
                           COUNT(m.machine_id) AS total_machines
                    FROM category c
                    LEFT JOIN product p ON c.category_code = p.category_code
                    LEFT JOIN machine m ON p.product_code = m.product_code
                    GROUP BY c.name, p.name
                """
            elif role in ['staff', 'lmgr'] and store_id is not None:
                query = """
                    SELECT c.name AS category_name, p.name AS product_name, 
                           COUNT(DISTINCT p.product_code) AS product_count, 
                           COUNT(m.machine_id) AS total_machines
                    FROM category c
                    LEFT JOIN product p ON c.category_code = p.category_code
                    LEFT JOIN machine m ON p.product_code = m.product_code
                    WHERE m.store_id = %s
                    GROUP BY c.name, p.name
                """
            else:
                return jsonify([])

            if role in ['staff', 'lmgr']:
                cursor.execute(query, (store_id,))
            else:
                cursor.execute(query)
            result = cursor.fetchall()
    return jsonify(result)

@app.route('/api/customer_orders')
def customer_orders():
    role = session.get('role', 'guest')
    store_id = session.get('store_id', None)

    with get_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            if role in ['admin', 'nmgr']:
                query = """
                    SELECT CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
                           COUNT(b.booking_id) AS order_count, 
                           COALESCE(SUM(b.total), 0) AS total_spent
                    FROM customer c
                    LEFT JOIN booking b ON c.customer_id = b.customer_id
                    GROUP BY c.customer_id, c.first_name, c.last_name
                """
            elif role in ['staff', 'lmgr'] and store_id is not None:
                query = """
                    SELECT CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
                           COUNT(b.booking_id) AS order_count, 
                           COALESCE(SUM(b.total), 0) AS total_spent
                    FROM customer c
                    LEFT JOIN booking b ON c.customer_id = b.customer_id
                    WHERE b.store_id = %s
                    GROUP BY c.customer_id, c.first_name, c.last_name
                """
            else:
                return jsonify([])

            if role in ['staff', 'lmgr']:
                cursor.execute(query, (store_id,))
            else:
                cursor.execute(query)
            result = cursor.fetchall()
    return jsonify(result)



@app.route('/api/store_distribution')
def store_distribution():
    with get_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            query = """
                SELECT city, COUNT(store_id) AS store_count
                FROM store
                GROUP BY city
            """
            cursor.execute(query)
            result = cursor.fetchall()
    return jsonify(result)


# User Roles Distribution / User Activity Distribution
@app.route('/users_report')
def users_report():
    allow_role(['admin'])
    return render_template('dashboard/users_report.html')

@app.route('/api/user_roles_distribution')
def user_roles_distribution():
    with get_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            query = """
                SELECT role, COUNT(*) as count
                FROM user where role !='nmgr'
                GROUP BY role
            """
            cursor.execute(query)
            result = cursor.fetchall()
    return jsonify(result)

@app.route('/api/user_activity_distribution')
def user_activity_distribution():
    with get_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            query = """
                SELECT is_active, COUNT(*) as count
                FROM user
                GROUP BY is_active
            """
            cursor.execute(query)
            result = cursor.fetchall()
    return jsonify(result)
