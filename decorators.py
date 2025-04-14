from functools import wraps
from flask import abort
from flask_login import current_user # Need current_user to check roles

# Role-Based Decorators
def admin_required(f):
    """Decorator to ensure user is logged in and is an admin."""
    @wraps(f) # Preserves original function metadata
    def decorated_function(*args, **kwargs):
        # Check if user is logged in AND if they have the admin role
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403) # Forbidden access
            # If checks pass, execute the original route function
        return f(*args, **kwargs)
    return decorated_function

def publisher_required(f):
    """Decorator to ensure user is logged in and is a publisher OR an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if not current_user.is_authenticated:
            abort(403) # Forbidden access if not logged in
            # Allow access if user is a publisher OR an admin
            # Uses the helper methods we defined in the User model
        if not current_user.is_publisher() and not current_user.is_admin():
            abort(403) # Forbidden access if not publisher or admin
        # If checks pass, execute the original route function
        return f(*args, **kwargs)
    return decorated_function

# Add any other custom decorators here later if needed
