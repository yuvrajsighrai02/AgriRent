from functools import wraps
from flask import session, abort

def logged_in():
    """
    Checks if a user is currently logged in by looking for 'loggedin' in the session.
    """
    return 'loggedin' in session

def allow_role(allowed_roles: list):
    """
    This is a decorator factory. It takes a list of roles that are permitted
    to access a specific route and returns a decorator.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            """
            This inner function runs only when a user accesses the decorated route.
            It checks for login status and role permission.
            """
            if not logged_in():
                # If the user is not logged in, return 401 Unauthorized.
                abort(401)

            user_role = session.get('role')
            if user_role not in allowed_roles:
                # If the user's role is not in the list of allowed roles, return 403 Forbidden.
                abort(403)
            
            # If all checks pass, proceed with the original route function.
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# The helper functions below are not directly causing the error, 
# but they can be simplified or used as needed.

def get_current_user_role():
    """
    Safely gets the role of the current user from the session.
    Returns None if the user is not logged in or has no role.
    """
    return session.get('role')

def check_user_role_customer():
    """Checks if the current user is a customer."""
    return get_current_user_role() == 'customer'

def check_user_role_staff():
    """Checks if the current user is staff."""
    return get_current_user_role() == 'staff'

def check_user_role_lmgr():
    """Checks if the current user is a local manager."""
    return get_current_user_role() == 'lmgr'

def check_user_role_nmgr():
    """Checks if the current user is a national manager."""
    return get_current_user_role() == 'nmgr'

def check_user_role_admin():
    """Checks if the current user is an admin."""
    return get_current_user_role() == 'admin'
