from flask import Flask, render_template, flash, redirect, url_for, request # Added render_template # Added flash, redirect, url_for, request # Add abort
from flask_sqlalchemy import SQLAlchemy # Added import
from flask_migrate import Migrate # Added import
from flask_login import LoginManager, current_user, login_required # Add current_user, login_required
from flask_misaka import Misaka
from flask_wtf.csrf import CSRFProtect # Import CSRFProtect

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

# Initialize CSRFProtect, will be configured with the app in create_app
csrf = CSRFProtect()

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
    Misaka(app) # Initialize Markdown rendering # Using default settings is usually fine
    csrf.init_app(app) # Initialize CSRF protection for the app

    # Import models AFTER db and login_manager have been initialized
    # This import order is now safe because db exists before models.py tries to import it
    from models import User, Department, MediaFile

    # Define user_loader (AFTER login_manager and User model are known)
    @login_manager.user_loader
    def load_user(user_id):
        """Callback function to load a user from the user ID stored in the session."""
        # user_id is stored as a string in the session, so convert to int for query
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.main import main_bp # Import the main Blueprint
    app.register_blueprint(main_bp) # Register it with the app

    from routes.auth import auth_bp # Import the auth Blueprint
    app.register_blueprint(auth_bp) # Register it

    from routes.notices import notice_bp # Import notice Blueprint
    app.register_blueprint(notice_bp)   # Register it

    from routes.events import event_bp   # Import event Blueprint
    app.register_blueprint(event_bp)    # Register it

    # Custom Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        """Handles 404 Not Found errors."""
        # Render a custom 404 template and return the 404 status code
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handles 403 Forbidden errors."""
        # Render a custom 403 template and return the 403 status code
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        """Handles 500 Internal Server errors."""
        # Important: Rollback the database session in case the error
        # occurred mid-transaction, leaving the session in a bad state.
        db.session.rollback()
        # Render a custom 500 template and return the 500 status code
        return render_template('errors/500.html'), 500

    return app # End of factory pattern (if using create_app function)

# Main execution
# This block ensures the server only runs when the script is executed directly
# (not when imported as a module) and enables debugging mode
if __name__ == '__main__':
    app = create_app() # Call the factory function to get the app instance
    app.run(debug=True) # Now run the created app instance # Debug=True is fine for development