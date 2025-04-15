# wsgi.py
from app import create_app

# Call the factory function to create the app instance
app = create_app()

# Optional: Add this block if you want to be able to run
# python wsgi.py directly for testing (similar to app.py)
# but it's not strictly needed for WSGI servers.
if __name__ == "__main__":
    app.run()
