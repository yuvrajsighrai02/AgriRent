from eoms import app
from flask import jsonify, request, session, redirect, url_for
from eoms.model import customer

# Module to check and update my store on customer facing pages

@app.before_request
def load_my_store():
    """
    This function runs before each request to load the user's preferred store.
    THE FIX: It now only sets the session from the database if the user has a 
    non-empty preferred store saved in their profile. This prevents it from
    overwriting a valid, temporary store selection with None for new users.
    """
    if 'my_store' not in session and session.get('customer_id'):
        user_profile = customer.get_my_store_by_customer_id(session['customer_id'])
        # Only set from DB if the value is not None
        if user_profile and user_profile.get('my_store'):
            session['my_store'] = user_profile.get('my_store')

@app.route('/update_my_store_session', methods=['POST'])
def update_my_store_session():
    """
    This is a new route specifically for the cart page.
    It allows the frontend to update the selected store in the session
    without needing a full page reload.
    """
    data = request.get_json()
    store_id = data.get('store_id')
    if store_id:
        session['my_store'] = int(store_id)
        # Also update the customer's permanent profile
        if 'customer_id' in session:
            customer.update_my_store_by_customer_id(session["customer_id"], store_id)
        return jsonify({'success': True, 'message': 'Store updated in session.'})
    return jsonify({'success': False, 'message': 'No store ID provided.'}), 400

# This function is kept for compatibility if used elsewhere
def update_my_store(store_id):
    if 'customer_id' in session:
        customer.update_my_store_by_customer_id(session["customer_id"], store_id)
    session['my_store'] = store_id
