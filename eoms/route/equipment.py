from eoms import app
from flask import render_template, redirect, request, flash, url_for, session, abort
from eoms.model import category, product, store
from eoms.form.product_shopping_form import ProductShoppingForm
from datetime import datetime
from eoms.model import stock

# This module handles ruotes of displaying lists of equipment and equipment

# View a list of equioment by category
@app.route('/for-hire/<category_code>')
def view_equipment_by_category(category_code):
    current_category = category.get_category_by_code(category_code)
    # Check if category exists
    if current_category and current_category.get('status') == 1:
        product_list = product.get_products_by_categroy(category_code)
    else:
        abort(404)
    return render_template('/shopping/equipment_list.html', equipment_list=product_list, current_category=current_category)

# Search equipment or view all equipment
@app.route('/for-hire')
def search_equipment():
    search_term = request.args.get('search')
    if search_term:
        product_list = product.search_product_by_name_desc(search_term)
        current_category = {'name': f'Search results for "{search_term}"'}
    else:
        current_category = {'name': 'All Equipment'}
        product_list = product.get_products_by_categroy(category_code=None)
    return render_template('/shopping/equipment_list.html', equipment_list=product_list, current_category=current_category)

# View the equipment detail
@app.route('/for-hire/<category_code>/<product_code>')
def view_equipment_detail(category_code, product_code):
    current_category = category.get_category_by_code(category_code)
    # Check if category exists
    if not current_category or current_category.get('status') == 0:
        abort(404)
    equipment = product.get_product_by_code(product_code)
    # Check if product exists
    if not equipment or equipment.get('status') == 0:
        abort(404)
    form = ProductShoppingForm()
    
    # Get the default store from session
    default_store_id = session.get('my_store')

    form.store.default = default_store_id
    form.product_code.data = product_code
    form.min_hire.data = equipment['min_hire']
    form.max_hire.data = equipment['max_hire']
    form.process()
    return render_template(
        '/shopping/equipment_detail.html',
        form=form,
        equipment=equipment,
        current_category=current_category)

