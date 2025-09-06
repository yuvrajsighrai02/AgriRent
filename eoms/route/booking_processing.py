from eoms import app
from flask import render_template, redirect, request, flash, url_for, session, jsonify
from markupsafe import Markup
from eoms.form.booking_form import BookingForm
from eoms.model import cart, customer, booking, cart_utils
from eoms.model.session_utils import allow_role, logged_in
from eoms.model.datetime_utils import datetime_to_nz

# Module for hanlding customer booking process


# Route for customer review complete booking after cart is validated
@app.route('/review_booking', methods=['POST'])
def review_booking():
    # Only registered customers can proceed to booking
    allow_role(['customer'])
    # Check if cart is validated 
    if cart_utils.is_cart_validated():
        cart_items = cart.get_cart_items_by_cart_id(session['cart_id'])
        booking_customer = customer.get_customer_by_user_id(session['user_id'])
        
        # Calculate totals
        original_total, total_discount, cart_total, total_gst = cart.get_cart_items_totals(cart_items)
        
        # Combine totals into a dictionary for easier access in the template
        totals = {
            'original_total': original_total,
            'total_discount': total_discount,
            'cart_total': cart_total,
            'total_gst': total_gst
        }

        promo_code = cart.get_cart_by_id(session['cart_id']).get('promo_code')
        if promo_code and not cart_utils.validate_promo_code(session['cart_id'], promo_code):
            flash(
                Markup(
                    'Promo code may become invalid or expired. You can continue booking or <a href="{}">go back to cart</a>.'.format(url_for('view_cart'))
                )
            )
        
        form = BookingForm(request.form)
        
        # THE FIX IS HERE: Pass the customer data with the key 'customer'
        return render_template(
            '/shopping/review_booking.html',
            cart_items=cart_items,
            totals=totals,
            customer=booking_customer, 
            form=form)
    # If cart is not validated, return back to shopping cart
    else:
        return redirect(url_for('view_cart'))

# Route to submit booking request  
@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    allow_role(['customer'])
    form = BookingForm(request.form)
    cart_id = session['cart_id']
    customer_id = session['customer_id']
    store_id = session['my_store']
    note = request.form.get('note', '')
    try:
    # Call the method for stored procedure and get the result message
        booking_id = booking.add_booking_by_cart_id(cart_id, customer_id, store_id, note)
        if booking_id:
            flash('Booking successful', 'success')
            return redirect(url_for('mybooking'))
        else:
            flash('Some items are no longer available for the selected hire period.', 'danger')
            return redirect(url_for('view_cart'))
    except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('view_cart'))
