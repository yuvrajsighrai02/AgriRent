from eoms import app
from flask import render_template, redirect, request, flash, url_for, session, jsonify
from eoms.form.login_form import LoginForm
from eoms.form.registration_form import RegistrationForm
from eoms.model import auth
from eoms.model import db
from eoms.model.session_utils import allow_role, logged_in
from eoms.model.booking import get_bookingList_by_date, get_bookingItemList_by_id, confirm_check_out, record_check_out
from eoms.model.product import select_all_from_product, add_new_equipment
from eoms.model.store import select_all_from_store, get_store_by_code
from eoms.model.upload import upload_image_by_product_code
# Import the entire message model with an alias to use the new functions
from eoms.model import message as message_model
from eoms.model.machine import get_machine_by_booking_item_ID
from datetime import datetime


@app.route('/addnew', methods=['GET', 'POST'])
def addNewEquipment():
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])

    productList = select_all_from_product()
    storeList = select_all_from_store()
    store = None  # ✅ Initialize store to avoid UnboundLocalError

    if 'store_id' in session and session['store_id']:
        store_id = session['store_id']
        store = get_store_by_code(store_id)

    if request.method == 'POST':
        product_code = request.form.get('product_code')
        sn = request.form.get('sn')
        store_id = request.form.get('store_id')
        purchase_date = request.form.get('purchase_date')
        cost = request.form.get('cost')
        image = request.files.get('upload_image')

        machine_id = add_new_equipment(
            product_code,
            sn,
            store_id,
            purchase_date,
            cost
        )

        if image:
            upload_image_by_product_code(machine_id, product_code, image)

        msg = "You have added new equipment successfully!"
        return render_template(
            'dashboard/addnew_equipment.html',
            msg=msg,
            productList=productList,
            storeList=storeList,
            store=store
        )

    return render_template(
        'dashboard/addnew_equipment.html',
        productList=productList,
        storeList=storeList,
        store=store
    )







@app.route('/dashboard')
def dashboard():
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    user_id = session['user_id']
    cursor = db.get_cursor()
    sql = 'SELECT * FROM staff left JOIN store ON store.store_id = staff.store_id WHERE user_id=%s;'
    cursor.execute(sql,(user_id,))
    user = cursor.fetchone()
    session['staff_id'] = user['staff_id']
    session['store_id'] = user['store_id']
    session['store_name'] = user['store_name']
    
    return render_template('dashboard/dashboard.html')

# --- THIS IS THE FIX ---
# The checkout function is now fully implemented.
# @app.route('/checkout', methods=['GET', 'POST'])
# def checkout():
#     allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    
#     # Determine the date to show bookings for. Default to today.
#     if request.method == 'POST':    
#         date = request.form.get('date')
#     else:
#         date = datetime.now().strftime('%Y-%m-%d')

#     # Get the list of bookings for the selected date
#     booking_list = get_bookingList_by_date(date)
    
#     # Organize the booking items by their booking ID
#     all_booking_items = {}
#     if booking_list:
#         booking_ids = [booking['booking_id'] for booking in booking_list]
#         booking_items_list = get_bookingItemList_by_id(booking_ids, date)
        
#         for item in booking_items_list:
#             booking_id = item['booking_id']
#             if booking_id not in all_booking_items:
#                 all_booking_items[booking_id] = []
#             all_booking_items[booking_id].append(item)

#     # Handle the confirmation of a checkout via an AJAX request
#     if request.method == 'POST' and request.form.get('id'):
#         booking_item_id = request.form.get('id')
#         staff_id = session['staff_id']
#         machine = get_machine_by_booking_item_ID(booking_item_id)
        
#         if machine:
#             confirm_check_out(machine['machine_id'])
#             record_check_out(booking_item_id, staff_id)
#             return jsonify({'status': 'success', 'message': 'Checkout confirmed'})
#         else:
#             return jsonify({'status': 'error', 'message': 'Machine not found'}), 404

#     # Render the checkout page with the booking data
#     return render_template(
#         'dashboard/checkout.html',
#         booking_list=booking_list,
#         all_booking_items=all_booking_items,
#         date=date
#     )


#New
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    date = datetime.now().strftime('%Y-%m-%d')
    user_id = session['user_id']

    # Get today's bookings
    bookingList = get_bookingList_by_date(date)
    booking_id_list = [booking['booking_id'] for booking in bookingList]
    bookingItemList = get_bookingItemList_by_id(booking_id_list, date)

    if request.method == 'POST':
        booking_item_id = request.form.get('id')
        machine = get_machine_by_booking_item_ID(booking_item_id)
        confirm_check_out(machine['machine_id'])   # Mark machine as checked-out
        record_check_out(booking_item_id, user_id) # Save checkout record
        return jsonify({'status': 'success', 'message': 'Checkout confirmed'})

    return render_template(
        'dashboard/checkout.html',
        bookingList=bookingList,
        bookingItemList=bookingItemList,
        date=date
    )







@app.route('/equipment_checkout_day', methods=['GET', 'POST'])
def equipment_checkout_day():
    allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
    bookingItemList = []
    if request.method == 'POST':
        date = request.form.get('date')
        bookingList = get_bookingList_by_date(date)
        booking_id_list = [booking['booking_id'] for booking in bookingList]
        bookingItemList = get_bookingItemList_by_id(booking_id_list, date)
    return render_template('dashboard/checkout.html', bookingList=bookingList, bookingItemList=bookingItemList, date=date)



#New
# @app.route('/addnew', methods=['GET', 'POST'])
# def addNewEquipment():
#     allow_role(['staff', 'lmgr', 'nmgr', 'admin'])

#     productList = select_all_from_product()
#     storeList = select_all_from_store()
#     store = None  # ✅ Initialize store to avoid UnboundLocalError

#     if 'store_id' in session and session['store_id']:
#         store_id = session['store_id']
#         store = get_store_by_code(store_id)

#     if request.method == 'POST':
#         product_code = request.form.get('product_code')
#         sn = request.form.get('sn')
#         store_id = request.form.get('store_id')
#         purchase_date = request.form.get('purchase_date')
#         cost = request.form.get('cost')
#         image = request.files.get('upload_image')

#         machine_id = add_new_equipment(
#             product_code,
#             sn,
#             store_id,
#             purchase_date,
#             cost
#         )

#         if image:
#             upload_image_by_product_code(machine_id, product_code, image)

#         msg = "You have added new equipment successfully!"
#         return render_template(
#             'dashboard/addnew_equipment.html',
#             msg=msg,
#             productList=productList,
#             storeList=storeList,
#             store=store
#         )

#     return render_template(
#         'dashboard/addnew_equipment.html',
#         productList=productList,
#         storeList=storeList,
#         store=store
#     )

# ==============================================================================
# STAFF MESSAGE CENTER ROUTES
# ==============================================================================

@app.route('/dashboard/messages', defaults={'thread_id': None})
@app.route('/dashboard/messages/<int:thread_id>')
@allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
def staff_messages(thread_id):
    """
    This is the new message center for staff.
    It displays a list of conversation threads and the selected conversation.
    """
    store_id = session.get('store_id')
    user_id = session.get('user_id')
    
    # Fetch all conversation threads for the staff member's store
    threads = message_model.get_threads_for_store(store_id)
    
    active_thread = None
    messages = []
    if thread_id:
        # Find the specific thread the user wants to view
        active_thread = next((t for t in threads if t['thread_id'] == thread_id), None)
        if active_thread:
            # Fetch all messages within that thread
            messages = message_model.get_messages_in_thread(thread_id, user_id)

    return render_template(
        'dashboard/message_center.html',
        threads=threads,
        messages=messages,
        active_thread=active_thread
    )

@app.route('/dashboard/messages/reply', methods=['POST'])
@allow_role(['staff', 'lmgr', 'nmgr', 'admin'])
def staff_reply_to_message():
    """Handles the staff's reply to a message thread."""
    user_id = session.get('user_id')
    thread_id = request.form.get('thread_id')
    reply_text = request.form.get('reply_text')

    if not all([thread_id, reply_text]):
        flash("Cannot send an empty reply.", "danger")
    else:
        # Use the new, correct function to add a reply
        success = message_model.add_reply_to_thread(thread_id, user_id, reply_text)
        if not success:
            flash("There was an error sending your reply.", "danger")
            
    # Redirect back to the conversation
    return redirect(url_for('staff_messages', thread_id=thread_id))
