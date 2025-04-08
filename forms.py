from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField # Add SelectField if allowing role selection during registration
# Import validators: DataRequired checks if field is not empty, Email checks format.
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError # Add EqualTo, ValidationError
from models import User # Import the User model to check for existing users

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

# We can add NoticeForm, etc., here later.
