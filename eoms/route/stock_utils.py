from eoms import app
from flask import jsonify, request
from eoms.model import machine

# Module to check stock level
@app.route('/check_stock', methods=['POST'])
def check_stock():
    data = request.json
    product_code = data['product_code']
    store_id = data['store_id']
    hire_from = data['hire_from']
    hire_to = data['hire_to']
    stock_level = len(machine.get_available_machines_by_code_store_date_range(product_code, store_id, hire_from, hire_to))
    # if stock_level == 0:
    #     status = "Out of Stock"
    # elif stock_level == 1:
    #     status = "Low Stock"
    # else:
    #     status = "In Stock"
    return jsonify({'stock': stock_level})


from eoms.model import machine

def get_available_stock(product_code, store_id, hire_from, hire_to):
    """Return available stock count for a product in a store within hire period."""
    return len(machine.get_available_machines_by_code_store_date_range(
        product_code, store_id, hire_from, hire_to
    ))
