from flask import Flask, render_template, flash, redirect, url_for, request, abort # Added render_template # Added flash, redirect, url_for, request # Add abort
from flask_sqlalchemy import SQLAlchemy # Added import
from flask_migrate import Migrate # Added import
from flask_login import LoginManager, login_user, logout_user, current_user, login_required # Add this # Add login_user, logout_user, current_user, login_required
from urllib.parse import urlparse, urljoin # Import for parsing the 'next' URL safely
from sqlalchemy import or_ # Import the 'or_' function
from functools import wraps

# Create Extension Instances (BEFORE app creation)
# We create them here but don't associate them with an app yet
# Create the SQLAlchemy database extension instance, but not linking it with our Flask app
db = SQLAlchemy()
# Create Flask-Migrate
migrate = Migrate()
# Create Flask-Login
login_manager = LoginManager()
# Tell Flask-Login which route handles logins
# 'login' is the FUNCTION NAME of the route we will create later
login_manager.login_view = 'login' # Name of the login route function
# Optional: Customize the message flashed when users need to log in
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info' # Bootstrap category for styling

# Application Factory Function (Optional but good practice)
# Or just create the app directly if you prefer for now
def create_app(): # Start of factory pattern
    app = Flask(__name__) # Create an instance of the Flask application

    # Load configuration from config.py
    app.config.from_pyfile('config.py')

    # Initialize Extensions with the App
    # Now we associate the extensions with our created app instance
    db.init_app(app) # Added initialization
    migrate.init_app(app, db) # Added initialization # Migrate needs both app and db
    login_manager.init_app(app) # Added initialization # Configure it for our app

    # Import models AFTER db and login_manager have been initialized
    # This import order is now safe because db exists before models.py tries to import it
    from models import User, Department, Notice, Event, MediaFile

    # Define user_loader (AFTER login_manager and User model are known)
    @login_manager.user_loader
    def load_user(user_id):
        """Callback function to load a user from the user ID stored in the session."""
        # user_id is stored as a string in the session, so convert to int for query
        return User.query.get(int(user_id))

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

    from forms import LoginForm, RegistrationForm # Import your form and model # Add RegistrationForm

    # Define a route for the homepage URL ('/')
    @app.route('/')
    def index():
        # This function runs when someone visits the homepage
        # Define the text we want to display in the heading
        welcome_heading = "Welcome to the College Event & Notice Board Portal!"
        # Render the index.html template, passing the heading text
        # The keyword 'heading' here MUST match the variable name {{ heading }} in the HTML
        return render_template('index.html', heading=welcome_heading)

    # Define a route for the login page URL ('/login')
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Handles user login."""
        # If user is already logged in, redirect to homepage
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        form = LoginForm() # Instantiate the form from forms.py
        if form.validate_on_submit(): # This runs only on POST requests where data is valid
            # Get the identifier entered by the user (could be username or email)
            identifier = form.username_or_email.data # Use the new field name

            # Query the database: find user where username OR email matches the identifier
            user = User.query.filter(or_(User.username == identifier, User.email == identifier)).first()

            # Check if user exists and password is correct
            if user and user.check_password(form.password.data):
                # Log the user in using Flask-Login's function
                login_user(user, remember=form.remember.data)
                flash('Logged in successfully!', 'success') # Optional success message

                # --- Redirect Logic ---
                # Get the URL the user was trying to access (if any)
                next_page = request.args.get('next')
                # Security check: Ensure next_page is a relative path within our site
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('index') # Default to index if no next_page or it's external

                # Check if the next_page is safe (optional but recommended)
                # This prevents open redirect vulnerabilities
                # You might need to adjust this check based on your specific needs
                # For now, we assume relative paths starting with '/' are safe
                if not next_page.startswith('/'):
                     next_page = url_for('index') # Fallback to index if unsure

                return redirect(next_page)
            else:
                # Invalid credentials
                flash('Invalid email or password. Please try again.', 'danger')
                # No redirect here, will re-render the login template below

        # If it's a GET request or form validation failed, display the login form
        return render_template('login.html', title='Sign In', form=form)

    # Define a route for the logout page URL ('/logout')
    @app.route('/logout')
    # @login_required # Ensure only logged-in users can access this # Commented out logout route decorator
    def logout():
        """Logs the current user out."""
        logout_user() # Flask-Login function to clear the session
        flash('You have been logged out.', 'info') # Optional message
        return redirect(url_for('index')) # Redirect to homepage

    # Define a route for the registration page URL ('/register')
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Handles user registration."""
        # If user is already logged in, redirect them away
        if current_user.is_authenticated:
            return redirect(url_for('index'))

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
            # Redirect the new user to the login page
            return redirect(url_for('login'))

        # If it's a GET request or validation failed, render the registration template
        return render_template('register.html', title='Register', form=form)

    return app # End of factory pattern (if using create_app function)

# Main execution
# This block ensures the server only runs when the script is executed directly
# (not when imported as a module) and enables debugging mode
if __name__ == '__main__':
    app = create_app() # Call the factory function to get the app instance
    app.run(debug=True) # Now run the created app instance # Debug=True is fine for development