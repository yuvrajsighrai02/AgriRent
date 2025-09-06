from eoms.model import machine
from eoms.model.db import get_cursor

def get_stock_availability(product_code, store_id, hire_from, hire_to):
    """
    Returns the number of available machines for a given product, store, and date range.
    An available machine is one with status = 1 (active) that is not booked
    during the specified period.
    """
    available_machines = machine.get_available_machines_by_code_store_date_range(
        product_code=product_code,
        store_id=store_id,
        date_from=hire_from,
        date_to=hire_to
    )
    return len(available_machines)

def get_total_quantity(product_code, store_id=None):
    """
    Gets the total number of machines for a product, regardless of status.
    If store_id is provided, it filters by store.
    """
    cursor = get_cursor()
    if store_id:
        query = "SELECT COUNT(*) as count FROM machine WHERE product_code = %s AND store_id = %s"
        cursor.execute(query, (product_code, store_id))
    else:
        query = "SELECT COUNT(*) as count FROM machine WHERE product_code = %s"
        cursor.execute(query, (product_code,))
    
    result = cursor.fetchone()
    return result['count'] if result else 0

def get_current_in_stock_count(product_code, store_id=None):
    """
    Gets the current number of machines with 'active' status (status = 1).
    This represents the total hireable fleet at this moment.
    If store_id is provided, it filters by store.
    """
    cursor = get_cursor()
    if store_id:
        query = "SELECT COUNT(*) as count FROM machine WHERE product_code = %s AND store_id = %s AND status = 1"
        cursor.execute(query, (product_code, store_id))
    else:
        query = "SELECT COUNT(*) as count FROM machine WHERE product_code = %s AND status = 1"
        cursor.execute(query, (product_code,))

    result = cursor.fetchone()
    return result['count'] if result else 0

