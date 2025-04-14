from flask import Flask, render_template, flash, redirect, url_for, request # Added render_template # Added flash, redirect, url_for, request # Add abort
from flask_sqlalchemy import SQLAlchemy # Added import
from flask_migrate import Migrate # Added import
from flask_login import LoginManager, current_user, login_required # Add current_user, login_required
from flask_misaka import Misaka

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
    Misaka(app) # Initialize Markdown rendering # Using default settings is usually fine

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

    return app # End of factory pattern (if using create_app function)

# Main execution
# This block ensures the server only runs when the script is executed directly
# (not when imported as a module) and enables debugging mode
if __name__ == '__main__':
    app = create_app() # Call the factory function to get the app instance
    app.run(debug=True) # Now run the created app instance # Debug=True is fine for development