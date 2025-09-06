from eoms import app
from flask import render_template, redirect, request, flash, url_for, session, jsonify
from eoms.form.login_form import LoginForm
from eoms.form.product_shopping_form import ProductShoppingForm
from eoms.model import cart, cart_utils, store, promotion
from eoms.route import my_store_utils
from eoms.model.session_utils import allow_role, logged_in
from eoms.model import stock

# Module for hanlding customer interactions with shopping cart

# Route to add items to shopping cart
@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    # Retrieve the data from the request
    form = ProductShoppingForm(request.form)
    if form.validate():
        cart_id = cart_utils.load_cart()
        my_store_utils.update_my_store(form.store.data)
        cart_items = cart.get_cart_items_by_cart_id(cart_id)
        # Check if product already in the cart with the same hire period
        # Update exisiting cart item if yes
        if cart_items:
            for cart_item in cart_items:
                if form.product_code.data == cart_item['product_code']\
                and form.hire_from.data == cart_item['hire_from']\
                and form.hire_to.data == cart_item['hire_to']:
                    cart.update_cart_item_by_id(cart_item_id=cart_item['cart_item_id'], qty=cart_item['qty']+1)
                    return jsonify({'success': True, 'message': 'Equipment has been added to cart'})
        # Add new cart item if not in cart
        response = cart.add_cart_items(
            cart_id, 
            form.product_code.data,
            1,
            form.hire_from.data, 
            form.hire_to.data
            )
        if response.get('status') == 'success':
            return jsonify({'success': True, 'message': response.get('message')})
        else:
            return jsonify({'success': False, 'message': response.get('message')}), 500
    else:
        return jsonify({"success": False, "message": form.errors}), 400

# Route to view shopping cart
@app.route('/cart')
def view_cart():
    cart_utils.load_cart()
    form = ProductShoppingForm(request.form)
    if cart.delete_outdated_cart_items_by_cart_id(session['cart_id']):
        flash('Some items were removed because hire dates were in the past.', 'warning')
    promo_code = cart.get_cart_by_id(session['cart_id']).get('promo_code')
    if promo_code and cart.apply_promo_to_cart(session['cart_id'], promo_code):
        flash('Discount has been applied to all eligible items in your shopping cart!', 'success')
    
    cart_items = cart.get_cart_items_by_cart_id(session['cart_id'])
    for item in cart_items:
        item['stock'] = stock.get_stock_availability(item['product_code'], session.get('my_store'), item['hire_from'], item['hire_to'])

    original_total, total_discount, cart_total, total_gst = cart.get_cart_items_totals(cart_items)
    store_list = store.get_all_active_stores()
    return render_template('/shopping/cart.html', 
                           cart_items=cart_items, 
                           cart_total=cart_total, 
                           total_discount=total_discount,
                           original_total=original_total,
                           total_gst=total_gst,
                           form=form, 
                           promo_code=promo_code,
                           store_list=store_list)

# Route to update shopping cart
@app.route('/cart/update', methods=['POST'])
def update_cart():
    data = request.get_json()
    cart_item_id = data.get('cart_item_id')
    new_qty = data.get('qty')
    if new_qty > 0 :
        cart.update_cart_item_by_id(cart_item_id=cart_item_id, qty=new_qty)
        cart_item = cart.get_cart_item_by_id(cart_item_id)
        if cart_item:
            cart_items = cart.get_cart_items_by_cart_id(cart_item['cart_id'])
            original_total, total_discount, cart_total, total_gst = cart.get_cart_items_totals(cart_items)
            return jsonify({
                'success': True,
                'cart_items': cart_items, 
                'cart_total': cart_total,
                'total_discount': total_discount,
                'original_total': original_total,
                'total_gst': total_gst
            })
        else:
            return jsonify({'success': False, 'message': 'Item not found.'})
    elif new_qty == 0:
        response = cart.delete_cart_item_by_id(cart_item_id)
        cart_items = cart.get_cart_items_by_cart_id(session['cart_id'])
        original_total, total_discount, cart_total, total_gst = cart.get_cart_items_totals(cart_items)
        if response.get('status') == 'success':
            return jsonify({'success': True, 
                            'message': response.get('message'),
                            'cart_items': cart_items, 
                            'cart_total': cart_total,
                            'total_discount': total_discount,
                            'original_total': original_total,
                            'total_gst': total_gst
                            })
        else:
            return jsonify({'success': False, 'message': response.get('message')}), 500
    else:
        return jsonify({'success': False, 'message': 'Invalid operation.'})

# Route to check and apply promo
@app.route('/apply_promo', methods=['POST'])
def apply_promo():
    promo_code = request.json.get('promo_code')
    cart_id = session.get('cart_id')
    if cart.apply_promo_to_cart(cart_id, promo_code):
        cart_items = cart.get_cart_items_by_cart_id(cart_id)
        original_total, total_discount, cart_total, total_gst = cart.get_cart_items_totals(cart_items)
        return jsonify({
            'success': True, 
            'cart_items': cart_items, 
            'cart_total': cart_total,
            'total_discount': total_discount,
            'original_total': original_total,
            'total_gst': total_gst,
            'message': 'Discount has been applied!'
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid or expired code, or no eligible items in cart. Please check again.'})

# Route to remove promo code
@app.route('/remove_promo', methods=['POST'])
def remove_promo():
    cart_id = session.get('cart_id')
    if cart.delete_promo_by_cart_id(cart_id):
        cart_items = cart.get_cart_items_by_cart_id(cart_id)
        original_total, total_discount, cart_total, total_gst = cart.get_cart_items_totals(cart_items)
        return jsonify({
            'success': True,
            'cart_items': cart_items,
            'original_total': original_total,
            'total_discount': total_discount,
            'total_gst': total_gst,
            'cart_total': cart_total,
            'message': 'Promo code removed.'
        })
    else:
        return jsonify({'success': False, 'message': 'Something went wrong. Please try again.'})

@app.route('/cart/stock_check')
def stock_check():
    cart_id = session.get('cart_id')
    if not cart_id:
        return jsonify({'success': False, 'error': 'Cart not found'})

    cart_items = cart.get_cart_items_by_cart_id(cart_id)
    stock_levels = {}
    for item in cart_items:
        stock_levels[item['cart_item_id']] = stock.get_stock_availability(
            item['product_code'],
            session.get('my_store'),
            item['hire_from'],
            item['hire_to']
        )
    return jsonify({'success': True, 'stock_levels': stock_levels})

