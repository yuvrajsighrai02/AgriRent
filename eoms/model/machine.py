from eoms.model.db import get_cursor
from flask import jsonify, abort

# Module to handle requey related to machine table
# Function to check stock availablitiy
# Return the number of avaliable machines for a given product and date range

def get_available_machines_by_code_store_date_range(product_code, store_id, date_from, date_to):
    """
    Checks for available machines for a given product, store, and date range.
    
    This function has been corrected with the proper logic to detect date range overlaps.
    It finds all machines for a product that are NOT booked during the requested period.
    A machine is considered booked if its rental period (hire_from, hire_to)
    overlaps in any way with the requested date range.
    """
    connection  = get_cursor()
    query = """
            SELECT * FROM machine
            WHERE product_code = %(product_code)s
            AND store_id = %(store_id)s
            AND status = 1 -- Only include active machines
            AND machine_id NOT IN (
                -- Subquery to find all machines that are UNAVAILABLE
                -- A machine is unavailable if it has a booking that overlaps
                -- with the requested hire period.
                SELECT machine_id 
                FROM booking_item
                WHERE 
                    -- THIS IS THE FIX: Corrected overlap logic
                    -- The booking starts BEFORE the requested end time
                    hire_from < %(date_to)s
                    AND
                    -- The booking ends AFTER the requested start time
                    hire_to > %(date_from)s
            )
            AND machine_id NOT IN (
                -- Also exclude machines scheduled for service
                SELECT machine_id
                FROM service
                WHERE service_date BETWEEN %(date_from)s AND %(date_to)s
            );
            """
    connection.execute(
        query, 
        {
            'product_code': product_code,
            'store_id': store_id,
            'date_from': date_from,
            'date_to': date_to
        }
    )
    available_machines = connection.fetchall()
    return available_machines


def get_machine_by_booking_item_ID(booking_item_id):
    connection  = get_cursor()
    query = """
            SELECT * FROM booking_item
            WHERE booking_item_id = %(booking_item_id)s;
            """
    connection.execute(
        query, 
        {
            'booking_item_id': booking_item_id,
        }
    )
    return connection.fetchone()
