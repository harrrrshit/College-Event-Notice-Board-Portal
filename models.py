from app import db # Import the db instance from app.py
from werkzeug.security import generate_password_hash, check_password_hash # Import the functions needed to hash and check passwords securely.
from flask_login import UserMixin # Import the necessary tools for user session management.

# Define the User model (represents the 'user' table in the database)
class User(db.Model, UserMixin): # Added UserMixin inheritance
    id = db.Column(db.Integer, primary_key=True) # Primary key column
    username = db.Column(db.String(35), unique=True, nullable=False) # Username, must be unique and not empty
    email = db.Column(db.String(120), unique=True, nullable=False) # Email, must be unique and not empty
    password_hash = db.Column(db.String(128)) # Stores the hashed password (length depends on hashing algorithm)
    role = db.Column(db.String(20), default='student', nullable=False) # User role ('student', 'publisher', 'admin'), defaults to 'student'
    # Foreign key to link to the Department table (optional, hence nullable=True)
    # 'department.id' refers to the 'id' column in the 'department' table (which we'll define later)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)

    # Define relationships (these don't create columns in the User table itself)
    # 'Notice' refers to the Notice class (we'll define later)
    # backref='poster' creates a virtual 'publisher' attribute on the Notice model to easily get the user who posted it
    # lazy=True means SQLAlchemy will load the related notices only when explicitly asked for
    notices = db.relationship('Notice', backref='publisher', lazy=True)
    # Similar relationship for Events
    events = db.relationship('Event', backref='organizer', lazy=True)

    # --- Password Hashing Methods ---
    def set_password(self, password):
        """Hashes the provided password and stores it."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256') # Using a strong method

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        # Returns True if passwords match, False otherwise.
        return check_password_hash(self.password_hash, password)

    # --- Role Checking Methods (Optional but useful for templates/routes) ---
    def is_admin(self):
        """Checks if the user has the 'admin' role."""
        return self.role == 'admin'

    def is_publisher(self):
        """Checks if the user has the 'publisher' role."""
        # Make sure 'publisher' is the exact string you store in the role column
        return self.role == 'publisher'

    # Optional: Define how User objects should be represented as strings (useful for debugging)
    def __repr__(self):
        return f'<User {self.username}>'

# Define the Department model (optional, but useful for organization)
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    # Relationships: A department can have multiple users, notices, and events
    # The 'department' backref allows access from User, Notice, Event objects (e.g., user.department)
    users = db.relationship('User', backref='department', lazy=True)
    notices = db.relationship('Notice', backref='department', lazy=True)
    events = db.relationship('Event', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'

# Define the Notice model
class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False) # Use db.Text for potentially long content
    # Use db.func.now() for a database-generated default timestamp
    issue_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    # Foreign key linking to the User who published the notice
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Foreign key linking to the Department (optional)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    # Relationship to potentially multiple media files
    # Added `cascade` option: This tells the database that if a Notice is deleted, all its associated MediaFile records should also be deleted automatically, which is usually desired.)
    media_files = db.relationship('MediaFile', backref='notice', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Notice {self.title}>'

# Define the Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False) # Date and time of the event
    venue = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True) # Optional category
    # Foreign key linking to the User who organized the event
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Foreign key linking to the Department (optional)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    # Relationship to potentially multiple media files
    # Added `cascade` option: This tells the database that if a Notice is deleted, all its associated MediaFile records should also be deleted automatically, which is usually desired.)
    media_files = db.relationship('MediaFile', backref='event', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Event {self.title}>'

# Define the MediaFile model
class MediaFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    # We could add a type later if needed ('image', 'video')
    # media_type = db.Column(db.String(20), nullable=False)

    # Foreign Key to link back to the Notice & Event it belongs to
    notice_id = db.Column(db.Integer, db.ForeignKey('notice.id'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)

    def __repr__(self):
        return f'<MediaFile {self.filename}>'
