from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user
from app import db # Import db from the main app module
from models import Notice, Department, User # Import necessary models
from forms import NoticeForm # Import the notice form
# Import decorators if they are defined in a central place, or redefine/import them
# Assuming decorators are defined in app.py for now, might need refactoring later
from decorators import publisher_required, admin_required # Adjust import if decorators move
from datetime import datetime, timedelta # Add these imports
from sqlalchemy import asc, desc # Import asc and desc from SQLAlchemy if not already implicitly available via db.session

# Define Blueprint
# All routes in this blueprint will be prefixed with /notices
notice_bp = Blueprint('notice', __name__, url_prefix='/notices')

# Notice Routes

# Route is now '/' relative to the '/notices' prefix -> /notices/
@notice_bp.route('/')
@login_required # All notice routes require login
def notice_list():
    # Displays a list of notices, with filtering and pagination.
    # Get Filter Parameters from URL (?department_id=X&start_date=Y&end_date=Z)
    # .get() is used to safely get parameters, providing None if they don't exist
    try:
        # Use type=int for department_id, handle potential ValueError if invalid input
        department_id = request.args.get('department_id', default=None, type=int)
        # Ensure 0 is treated as None (our 'All Departments' value from the form)
        if department_id == 0:
            department_id = None
    except ValueError:
        flash('Invalid Department ID provided.', 'warning')
        department_id = None

    start_date_str = request.args.get('start_date', default=None)
    end_date_str = request.args.get('end_date', default=None)

    # Get Sorting Parameters
    sort_by = request.args.get('sort_by', 'date') # Default sort by date
    sort_order = request.args.get('sort_order', 'desc') # Default descending (newest first)

    # Build Base Query
    query = Notice.query # Start with query for all Notices

    # Apply Filters
    start_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(Notice.issue_date >= start_date)
        except ValueError:
            flash('Invalid start date format. Please use YYYY-MM-DD.', 'warning')
            start_date_str = None # Clear invalid input for display

    end_date = None
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # To include notices ON the end date, filter for less than the *next* day
            query = query.filter(Notice.issue_date < end_date + timedelta(days=1))
        except ValueError:
            flash('Invalid end date format. Please use YYYY-MM-DD.', 'warning')
            end_date_str = None # Clear invalid input for display

    if department_id:
        # Ensure the department actually exists before filtering (optional safety check)
        dept_exists = Department.query.get(department_id)
        if dept_exists:
            query = query.filter(Notice.department_id == department_id)
        else:
            flash(f'Department ID {department_id} not found.', 'warning')
            department_id = None # Reset filter if department doesn't exist

    # Apply Sorting (Newest first by default)
    if sort_by == 'title':
        order_column = Notice.title
    elif sort_by == 'department':
         # Join with Department table to sort by department name
         # outerjoin is safer if a notice might not have a department
        query = query.outerjoin(Department)
        order_column = Department.name
    else: # Default to sorting by date
        sort_by = 'date' # Ensure sort_by reflects the default
        order_column = Notice.issue_date

    # Apply sort order (ascending or descending)
    if sort_order == 'asc':
        query = query.order_by(asc(order_column))
    else:
        sort_order = 'desc' # Default to desc if invalid value passed
        query = query.order_by(desc(order_column))

    # Pagination
    # Get page number from URL query string (?page=N), default to 1
    page = request.args.get('page', 1, type=int)
    # Use paginate instead of .all()
    # per_page: how many items per page (adjust as needed)
    # error_out=False: prevents 404 error if page number is invalid, shows empty page instead
    try:
        pagination = query.paginate(page=page, per_page=10, error_out=False)
    except Exception as e:
        # Handle potential database errors during pagination
        flash(f'Error retrieving notices: {e}', 'danger')
        pagination = None
        notices = []

    if pagination:
        notices = pagination.items # Get the list of items for the current page
    else:
        notices = [] # Ensure notices is an empty list if pagination failed

    # Get Data for Filter Form
    # Fetch departments only if needed (e.g., if the query succeeded)
    departments = Department.query.order_by(Department.name).all() if pagination else []

    # Store current filters and sorting to pass back to template
    # Ensure values passed back are safe/valid, using None if parsing failed
    current_params = {
        'department_id': department_id if department_id is not None else 0,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'sort_by': sort_by,
        'sort_order': sort_order
    }

    return render_template(
        'notice_list.html',
        title='Notices',
        notices=notices, # Pass the items for the current page
        pagination=pagination, # Pass the pagination object for page links
        departments=departments, # Pass departments for the dropdown
        current_params=current_params # Pass combined params
    )

# Route is now '/<int:notice_id>' relative to '/notices' -> /notices/123
@notice_bp.route('/<int:notice_id>')
@login_required
def notice_detail(notice_id):
    """Displays the details of a single notice."""
    # Get the notice by ID, or return a 404 Not Found error if it doesn't exist
    notice = Notice.query.get_or_404(notice_id)
    return render_template('notice_detail.html', title=notice.title, notice=notice)

# Route is now '/new' relative to '/notices' -> /notices/new
@notice_bp.route('/new', methods=['GET', 'POST'])
@login_required
@publisher_required # Only publishers or admins can create # Use the imported decorator
def notice_create():
    """Handles creation of a new notice."""
    form = NoticeForm()
    if form.validate_on_submit():
        # Create new Notice object
        notice = Notice(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id # Set the publisher to the current user
        )
        # Handle optional department ID (0 means 'None' selected)
        if form.department_id.data and form.department_id.data > 0:
            notice.department_id = form.department_id.data
        else:
            notice.department_id = None # Explicitly set to None if 0 or not provided

        db.session.add(notice)
        db.session.commit()
        flash('Your notice has been posted!', 'success')
        # Use namespaced endpoint for redirect
        return redirect(url_for('notice.notice_list')) # Redirect to the list view

    # If GET request or form validation failed
    return render_template('notice_form.html', title='Post New Notice', form=form, legend='New Notice')

# Route is now '/<int:notice_id>/edit' -> /notices/123/edit
@notice_bp.route('/<int:notice_id>/edit', methods=['GET', 'POST'])
@login_required # Must be logged in
def notice_edit(notice_id):
    """Handles editing an existing notice."""
    notice = Notice.query.get_or_404(notice_id)

    # Permission Check
    if not current_user.is_admin() and notice.user_id != current_user.id:
        # If the current user is NOT an admin AND they are NOT the original publisher
        abort(403) # Forbidden

    # Pass obj=notice to pre-populate form fields with existing data on GET
    form = NoticeForm(obj=notice)

    if form.validate_on_submit(): # Runs on POST if data is valid
        # Update the existing notice object's fields
        notice.title = form.title.data
        notice.content = form.content.data
        if form.department_id.data and form.department_id.data > 0:
            notice.department_id = form.department_id.data
        else:
            notice.department_id = None
        # Record the current user as the editor to track last editor.
        notice.last_edited_by_id = current_user.id
        # No need for db.session.add(notice) because the object is already tracked
        db.session.commit()
        flash('Your notice has been updated!', 'success')
        # Use namespaced endpoint for redirect
        return redirect(url_for('notice.notice_detail', notice_id=notice.id)) # Redirect to detail view

    # If GET request, the form is already pre-populated via obj=notice
    # If POST failed validation, it will render with errors
    return render_template('notice_form.html', title='Edit Notice', form=form, legend='Edit Notice')

# Route is now '/<int:notice_id>/delete' -> /notices/123/delete
@notice_bp.route('/<int:notice_id>/delete', methods=['POST'])
@login_required # Must be logged in
def notice_delete(notice_id):
    """Handles deleting a notice."""
    notice = Notice.query.get_or_404(notice_id)

    # Permission Check
    if not current_user.is_admin() and notice.user_id != current_user.id:
        # If the current user is NOT an admin AND they are NOT the original publisher
        abort(403) # Forbidden

    # Delete media files associated with the notice first (if cascade isn't working or for explicit control)
        # Note: The cascade="all, delete-orphan" on the relationship *should* handle this automatically
        # for media_file in notice.media_files:
        #     db.session.delete(media_file)
            # Optionally delete the actual file from disk here too

    db.session.delete(notice)
    db.session.commit()
    flash('Notice has been deleted!', 'success')
    # Use namespaced endpoint for redirect
    return redirect(url_for('notice.notice_list')) # Redirect to the list view
