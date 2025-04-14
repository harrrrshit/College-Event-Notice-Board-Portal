from flask import Blueprint, render_template
# Import current_user if needed for display, though index doesn't use it heavily yet
from flask_login import current_user

# Create a Blueprint instance named 'main'
# The first argument 'main' is the Blueprint's name, used in url_for
# The second argument __name__ helps locate resources
main_bp = Blueprint('main', __name__)

# Define the route for the homepage URL ('/') using the Blueprint
@main_bp.route('/')
def index():
    # This function runs when someone visits the homepage
    # Define the text we want to display in the heading
    welcome_heading = "Welcome to the College Event & Notice Board Portal!"
    # Render the index.html template, passing the heading text
    # The keyword 'heading' here MUST match the variable name {{ heading }} in the HTML
    # Note: We might move the logic for fetching recent notices/events here later (Phase 5)
    return render_template('index.html', heading=welcome_heading)

# Add other main/static routes here later if needed (e.g., about page)
