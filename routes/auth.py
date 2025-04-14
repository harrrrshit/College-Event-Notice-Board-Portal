from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user # Removed login_required for now as it's not used directly here yet
from sqlalchemy import or_
from urllib.parse import urlparse # Import for parsing the 'next' URL safely # Removed urljoin as it wasn't used

# Import necessary components from the main app structure
# We need db for database queries and models/forms
from app import db
from models import User
from forms import LoginForm, RegistrationForm

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth') # Optional: Add a URL prefix

# Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    # If user is already logged in, redirect to homepage
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Use main blueprint endpoint

    form = LoginForm() # Instantiate the form from forms.py
    if form.validate_on_submit(): # This runs only on POST requests where data is valid
        # Get the identifier entered by the user (could be username or email)
        identifier = form.username_or_email.data # Use the new field name

        # Query the database: find user where username OR email matches the identifier
        user = User.query.filter(
            or_(User.username == identifier, User.email == identifier)
        ).first()

        # Check if user exists and password is correct
        if user and user.check_password(form.password.data):
            # Log the user in using Flask-Login's function
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully!', 'success')

            # Redirect Logic
            # Get the URL the user was trying to access (if any)
            next_page = request.args.get('next')
            # Basic Security check: Ensure next_page is a relative path within our site
            # Check if the next_page is safe (optional but recommended)
            # This prevents open redirect vulnerabilities
            # You might need to adjust this check based on your specific needs
            # For now, we assume relative paths starting with '/' are safe
            if not next_page or urlparse(next_page).netloc != '' or not next_page.startswith('/'):
                next_page = url_for('main.index') # Default to main.index if no next_page or it's external # Fallback to index if unsure # Use main blueprint endpoint

            return redirect(next_page)
        else:
            # Invalid credentials
            flash('Invalid username/email or password. Please try again.', 'danger')
            # No redirect here, will re-render the login template below

    # If it's a GET request or form validation failed, display the login form
    return render_template('login.html', title='Sign In', form=form)

# Logout Route
@auth_bp.route('/logout')
# @login_required # Ensure only logged-in users can access this # Commented out logout route decorator
def logout():
    """Logs the current user out."""
    logout_user() # Flask-Login function to clear the session
    flash('You have been logged out.', 'info') # Message
    return redirect(url_for('main.index')) # Redirect to homepage # Use main blueprint endpoint

# Registration Route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    # If user is already logged in, redirect them away
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Use main blueprint endpoint

    form = RegistrationForm() # Instantiate the registration form
    if form.validate_on_submit(): # Runs on POST if validators (including custom ones) pass
        # Create a new User object (role defaults to 'student' if not included in form)
        user = User(username=form.username.data, email=form.email.data)
        # Set the password using the method that handles hashing
        user.set_password(form.password.data)
        # Add the new user object to the database session
        db.session.add(user)
        # Commit the session to save the user permanently
        db.session.commit()
        # Flash a success message
        flash('Congratulations, you are now a registered user! Please log in.', 'success')
        # Redirect to the login page WITHIN this blueprint
        return redirect(url_for('auth.login')) # Use auth blueprint endpoint

    # If it's a GET request or validation failed, render the registration template
    return render_template('register.html', title='Register', form=form)
