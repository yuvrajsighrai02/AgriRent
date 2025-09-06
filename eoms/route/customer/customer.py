from eoms import app
from flask import render_template, redirect, request, flash, url_for, session, jsonify
from eoms.model import db, store
from eoms.model.session_utils import allow_role
from eoms.form.booking_form import BookingForm
# THE FIX: Import the extend_booking_period function
from eoms.model.booking import get_my_current_booking, get_bookingItemList, get_my_current_booking_notEarlyToday, cancel_booking_byuserIdAndBookingId, extend_booking_period
from eoms.model import message as message_model
import stripe
from datetime import datetime

# ==============================================================================
# BOOKING ROUTES
# ==============================================================================

@app.route('/mybooking', methods=['GET', 'POST'])
@allow_role(['customer'])
def mybooking():
    """
    Displays the customer's current and upcoming bookings.
    """
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for('login'))

    form = BookingForm()

    booking_list = get_my_current_booking_notEarlyToday(user_id)
    allBookingList = {}
    if booking_list:
        for booking in booking_list:
            booking_items = get_bookingItemList(booking['booking_id'])
            allBookingList[booking['booking_id']] = {
                'create_date': booking['create_date'],
                'status': booking['status'],
                'booking_items': booking_items if booking_items else []
            }
    
    return render_template('customer/mybooking.html', booking_list=booking_list, allBookingList=allBookingList, form=form)


#Old code is good but show allbooking means current also in history.
# @app.route('/allbooking', methods=['GET', 'POST'])
# @allow_role(['customer'])
# def allbooking():
#     """
#     Displays the customer's entire booking history.
#     """
#     user_id = session.get("user_id")
#     if not user_id:
#         return redirect(url_for('login'))
        
#     form = BookingForm()

#     booking_list = get_my_current_booking(user_id)
#     allBookingList = {}
#     if booking_list:
#         for booking in booking_list:
#             booking_items = get_bookingItemList(booking['booking_id'])
#             allBookingList[booking['booking_id']] = {
#                 'create_date': booking['create_date'],
#                 'status': booking['status'],
#                 'booking_items': booking_items if booking_items else []
#             }

#     return render_template('customer/allbooking.html', booking_list=booking_list, allBookingList=allBookingList, form=form)


#New
@app.route('/allbooking', methods=['GET', 'POST'])
@allow_role(['customer'])
def allbooking():
    """
    Displays the customer's booking history (completed + cancelled only).
    """
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for('login'))

    form = BookingForm()

    booking_list = get_my_current_booking(user_id)
    
    # ✅ Filter: keep only completed (1) or cancelled (-1)
    filtered_list = [b for b in booking_list if b['status'] in (1, -1)]

    allBookingList = {}
    if filtered_list:
        for booking in filtered_list:
            booking_items = get_bookingItemList(booking['booking_id'])
            allBookingList[booking['booking_id']] = {
                'create_date': booking['create_date'],
                'status': booking['status'],
                'booking_items': booking_items if booking_items else []
            }

    return render_template(
        'customer/allbooking.html',
        booking_list=filtered_list,
        allBookingList=allBookingList,
        form=form
    )






@app.route('/cancelBooking/<int:id>', methods=['GET', 'POST'])
@allow_role(['customer'])
def cancelbooking(id):
    """
    Allows a customer to cancel a booking.
    """
    customer_id = session.get('customer_id')
    if customer_id:
        cancel_booking_byuserIdAndBookingId(customer_id, id)
        flash('Your booking has been cancelled.', 'success')
    return redirect(url_for('mybooking'))

# ==============================================================================
# NEW ROUTE FOR EXTENDING BOOKING PERIOD
# ==============================================================================
@app.route('/extendperiod/<int:id>', methods=['POST'])
@allow_role(['customer'])
def extendperiod(id):
    """
    Handles the request to extend a booking period for a single item.
    """
    booking_item_id = id
    hire_to = request.form.get('hire_to')
    
    if not hire_to:
        return jsonify({'success': False, 'error': 'New end date is missing.'}), 400
    
    # The model function returns a JSON response, so we can return it directly.
    # Note: In a larger refactor, it would be better for the model to return True/False
    # and have the route build the JSON response.
    return extend_booking_period(hire_to, booking_item_id)


# ==============================================================================
# MESSAGE CENTER ROUTES
# ==============================================================================

@app.route('/messages', defaults={'thread_id': None})
@app.route('/messages/<int:thread_id>')
@allow_role(['customer'])
def messages(thread_id):
    customer_id = session.get('customer_id')
    user_id = session.get('user_id')
    
    threads = message_model.get_threads_for_customer(customer_id)
    
    active_thread = None
    messages = []
    if thread_id:
        active_thread = next((t for t in threads if t['thread_id'] == thread_id), None)
        if active_thread:
            messages = message_model.get_messages_in_thread(thread_id, user_id)

    return render_template(
        'customer/message_center.html',
        threads=threads,
        messages=messages,
        active_thread=active_thread
    )

@app.route('/messages/new', methods=['GET', 'POST'])
@allow_role(['customer'])
def new_message_thread():
    if request.method == 'POST':
        customer_id = session.get('customer_id')
        user_id = session.get('user_id')
        store_id = request.form.get('store_id')
        subject = request.form.get('subject')
        content = request.form.get('content')

        if not all([store_id, subject, content]):
            flash("All fields are required.", "danger")
            return redirect(url_for('new_message_thread'))

        thread_id = message_model.create_new_thread(customer_id, store_id, subject, content, user_id)
        if thread_id:
            flash("Your message has been sent.", "success")
            return redirect(url_for('messages', thread_id=thread_id))
        else:
            flash("There was an error sending your message.", "danger")
    
    stores = store.get_all_active_stores()
    return render_template('customer/new_message.html', stores=stores)

@app.route('/messages/reply', methods=['POST'])
@allow_role(['customer'])
def reply_to_message():
    user_id = session.get('user_id')
    thread_id = request.form.get('thread_id')
    reply_text = request.form.get('reply_text')

    if not all([thread_id, reply_text]):
        flash("Cannot send an empty reply.", "danger")
    else:
        success = message_model.add_reply_to_thread(thread_id, user_id, reply_text)
        if not success:
            flash("There was an error sending your reply.", "danger")
            
    return redirect(url_for('messages', thread_id=thread_id))

@app.route('/create-extension-payment-intent', methods=['POST'])
@allow_role(['customer'])
def create_extension_payment_intent():
    """
    Creates a Stripe PaymentIntent for extending a booking.
    """
    try:
        data = request.get_json()
        booking_item_id = data.get('booking_item_id')
        new_hire_to_str = data.get('new_hire_to')
        daily_rate = float(data.get('daily_rate'))
        
        # Find the original booking item to get the old hire_to date
        cursor = db.get_cursor()
        cursor.execute("SELECT hire_to FROM booking_item WHERE booking_item_id = %s", (booking_item_id,))
        booking_item = cursor.fetchone()
        if not booking_item:
            return jsonify({'error': 'Booking item not found'}), 404

        # Calculate the number of extra days
        old_hire_to = booking_item['hire_to']
        new_hire_to = datetime.fromisoformat(new_hire_to_str)
        extension_days = (new_hire_to - old_hire_to).days

        if extension_days <= 0:
            return jsonify({'error': 'New date must be after the current end date.'}), 400

        # Calculate the cost and create the payment intent
        total_cost = extension_days * daily_rate
        amount_in_paise = int(total_cost * 100)

        intent = stripe.PaymentIntent.create(
            amount=amount_in_paise,
            currency='inr',
            automatic_payment_methods={'enabled': True},
            metadata={
                'payment_type': 'extension', # Identify this as an extension payment
                'booking_item_id': booking_item_id,
                'new_hire_to': new_hire_to_str
            }
        )
        return jsonify({'clientSecret': intent.client_secret, 'total_cost': total_cost})
    except Exception as e:
        return jsonify(error=str(e)), 403