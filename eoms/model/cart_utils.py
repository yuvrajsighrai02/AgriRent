from eoms import app
from flask import render_template, redirect, request, flash, url_for, session, jsonify
from eoms.model import cart, machine
from eoms.model.session_utils import allow_role, logged_in


# Module to load shopping cart
def load_cart():
    if 'cart_id' not in session:
        # Fetch customer's shopping cart if customer is logged in
        if 'customer_id' in session:
            customer_cart = cart.get_cart_by_customer_id(session['customer_id'])
            cart_id = customer_cart['cart_id']
            if not cart_id:
                cart_id = cart.add_cart(session['customer_id'])
        else:
            cart_id = cart.add_cart()
        session['cart_id'] = cart_id
    return session['cart_id']

# Module to check if customer has been assigned to a cart as well as a guest cart
# Merge the cart if both found
def merge_customer_cart(customer_id):
    cutomer_cart = cart.get_cart_by_customer_id(customer_id)
    customer_cart_items = cart.get_cart_items_by_cart_id(cutomer_cart['cart_id'])
    if session.get('cart_id'):
        if cutomer_cart['cart_id'] != session.get('cart_id'):
            guest_cart = cart.get_cart_by_id(session['cart_id'])
            promo_code = guest_cart['promo_code']
            guest_cart_items = cart.get_cart_items_by_cart_id(session['cart_id'])
            for guest_item in guest_cart_items:
                customer_cart_id = cutomer_cart['cart_id']
                product_code = guest_item['product_code']
                # If it's the same product with exact same hire period, update the qty
                for customer_item in customer_cart_items:
                    if customer_item['product_code'] == guest_item['product_code'] \
                        and customer_item['hire_from'] == guest_item['hire_from']\
                        and customer_item['hire_to'] == guest_item['hire_to']:
                        cart.update_cart_item_by_id(
                            customer_item['cart_item_id'], 
                            qty=customer_item['cart_item_id']+guest_item['cart_item_id']
                            )
                cart.add_cart_items(
                    cutomer_cart['cart_id'], 
                    guest_item['product_code'], 
                    guest_item['qty'], 
                    guest_item['hire_from'], 
                    guest_item['hire_to']
                    )
            # Apply promo 
            if promo_code:
                cart.apply_promo_to_cart(cutomer_cart['cart_id'], promo_code)
    session['cart_id'] = cutomer_cart['cart_id']
# Module to validate shopping cart, 
# update shopping cart when not all stock is available

def is_cart_validated():
    # Get cart_id from session
    cart_id = session.get('cart_id')
    # Get store_id from session
    store_id = session.get('my_store')
    # Validate cart_id exists
    if not cart_id:
        flash('Shopping cart not fouund, please try again.', 'danger')
        return False
    # Validate store_id exists
    if not store_id:
        flash('Please select a store', 'danger')
        return False
    # Fetch cart items
    cart_items = cart.get_cart_items_by_cart_id(cart_id)
    # Validate cart items exist
    if not cart_items:
        flash('Shopping cart is empty, did you forget something?', 'danger')
        return False
    # Remove any outdated cart items
    if cart.delete_outdated_cart_items_by_cart_id(cart_id):
        flash('Some items were removed because hire dates were in the past.', 'warning')
        return False
    # Check each cart item availability
    cart_updated = False
    for cart_item in cart_items:
        available_machines = machine.get_available_machines_by_code_store_date_range(
            product_code=cart_item['product_code'],
            store_id=store_id,
            date_from=cart_item['hire_from'],
            date_to=cart_item['hire_to']
        )
        # No stock available, remove item from cart
        if len(available_machines) == 0:
            cart.delete_cart_item_by_id(cart_item['cart_item_id'])
            flash(f"No stock available for {cart_item['product_code']}", 'danger')
            cart_updated = True
        # Avaialble stock is less than QTY needed, update QTY
        elif len(available_machines) < cart_item['qty']:
            cart.update_cart_item_by_id(cart_item['cart_item_id'], qty=len(available_machines))
            flash(f"Only {len(available_machines)} in stock for {cart_item['product_code']}", 'warning')
            cart_updated = True
        # Stock available, check the next one
    # Return True if cart is not updated, i.e. all stockk available
    # Return False if not all stock avaialble and cart needs updated
    return not cart_updated

# Check if promo code is still valid
def validate_promo_code(cart_id, promo_code):
    # Remove promo and re-apply
    cart.delete_promo_by_cart_id(cart_id)
    appied_promo = cart.apply_promo_to_cart(cart_id, promo_code)
    return appied_promo