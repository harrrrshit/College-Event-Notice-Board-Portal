from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateTimeField # Add TextAreaField, SelectField # Add DateTimeField
# Import validators: DataRequired checks if field is not empty, Email checks format.
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError # Add EqualTo, ValidationError
from models import User, Department # Import the User model to check for existing users # Import Department if using department selection
from datetime import datetime # Add this import

# Define the login form structure and validation rules
class LoginForm(FlaskForm):
    # Using Username or Email field for login as per User model.
    # Label is 'Username or Email', validators ensure it's provided and is a valid email.
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()]) # Password field. Label is 'Password', validator ensures it's provided.
    remember = BooleanField('Remember Me') # Optional 'Remember Me' checkbox.
    submit = SubmitField('Login') # Submit button for the form. Label is 'Login'.

# Define the registration form structure and validation rules
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=35, message='Username must be between 3 and 35 characters.')])
    email = StringField('Email', validators=[DataRequired(), Email(message='Enter a valid email.')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long.')])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]) # EqualTo checks if this field matches the 'password' field
    # Optional: Allow role selection during registration (maybe only show for admins later?)
    # For now, let's include it but default registration might just be 'student'
    # role = SelectField('Role', choices=[('student', 'Student'), ('publisher', 'Publisher'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Register')

    # --- Custom Validators ---
    # WTForms automatically uses methods named validate_<fieldname>

    def validate_username(self, username):
        """Check if username already exists."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        """Check if email already exists."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email address already registered. Please use a different one.')

# Define the notice form structure and validation rules
class NoticeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"rows": 7})
    # Optional: Department Selection
    # coerce=int ensures the value submitted is treated as an integer
    department_id = SelectField('Department (Optional)', coerce=int)
    submit = SubmitField('Post Notice') # Label might change for editing

    # --- Populate Department Choices ---
    # We need to populate the choices for the department dropdown dynamically
    def __init__(self, *args, **kwargs):
        super(NoticeForm, self).__init__(*args, **kwargs)
        # Query all departments ordered by name
        # Set choices: list of tuples (value, label)
        # Start with a "None" option (value 0, assuming 0 is not a valid dept ID)
        self.department_id.choices = [(0, '--- Select Department ---')] + \
                                     [(dept.id, dept.name) for dept in Department.query.order_by(Department.name).all()]

# Define the event form structure and validation rules
class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()], render_kw={"rows": 10})
    # DateTimeField for date and time input.
    # format='%Y-%m-%dT%H:%M' matches the standard HTML datetime-local input format.
    event_date = DateTimeField('Event Date and Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired(), Length(max=100)])
    # Category selection - predefined choices
    category = SelectField('Category', choices=[
        ('', '-- Select Category --'), # Optional placeholder
        ('Academic', 'Academic'),
        ('Cultural', 'Cultural'),
        ('Sports', 'Sports'),
        ('Workshop', 'Workshop'),
        ('Seminar', 'Seminar'),
        ('Other', 'Other')
    ], validators=[DataRequired(message='Please select a category.')]) # Made category required
    # Optional: Department Selection (same as NoticeForm)
    department_id = SelectField('Organizing Department (Optional)', coerce=int)
    submit = SubmitField('Post Event') # Label might change for editing

    # --- Populate Department Choices ---
    # Same logic as NoticeForm to populate the dropdown
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # Query all departments ordered by name
        # Set choices: list of tuples (value, label)
        # Start with a "None" option (value 0)
        self.department_id.choices = [(0, '--- Select Department ---')] + \
                                     [(dept.id, dept.name) for dept in Department.query.order_by(Department.name).all()]

    # Custom Validator for Event Date
    def validate_event_date(self, field):
        """Ensure the event date is not in the past."""
        # field.data should be a datetime object if format parsing succeeded
        if field.data and field.data < datetime.now():
            # Raise ValidationError if the date is before the current moment
            raise ValidationError('Event date and time cannot be in the past.')



