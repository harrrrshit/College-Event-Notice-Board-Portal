from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user
from app import db
from models import Event, Department, User # Import Event model
from forms import EventForm # Import Event form
from decorators import publisher_required, admin_required # Import decorators # Adjust import if decorators move
from datetime import datetime, timedelta
from sqlalchemy import asc, desc # Add asc, desc, datetime, timedelta

# Define Blueprint
event_bp = Blueprint('event', __name__, url_prefix='/events')

# Event Routes

# Route -> /events/
@event_bp.route('/')
@login_required
def event_list():
    """Displays a list of all events, with filtering, sorting, and pagination."""
    # --- Get Filter Parameters ---
    try:
        department_id = request.args.get('department_id', default=None, type=int)
        if department_id == 0: department_id = None
    except ValueError:
        flash('Invalid Department ID provided.', 'warning')
        department_id = None

    start_date_str = request.args.get('start_date', default=None)
    end_date_str = request.args.get('end_date', default=None)
    category = request.args.get('category', default=None) # Get category filter

    # --- Get Sorting Parameters ---
    sort_by = request.args.get('sort_by', 'date') # Default sort by event date
    sort_order = request.args.get('sort_order', 'asc') # Default ascending (upcoming first)

    # --- Build Base Query ---
    query = Event.query

    # --- Apply Filters ---
    start_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            # Filter events where event_date is on or after start_date
            query = query.filter(Event.event_date >= start_date)
        except ValueError:
            flash('Invalid start date format. Please use YYYY-MM-DD.', 'warning')
            start_date_str = None

    end_date = None
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # Filter events where event_date is before the day *after* end_date
            query = query.filter(Event.event_date < end_date + timedelta(days=1))
        except ValueError:
            flash('Invalid end date format. Please use YYYY-MM-DD.', 'warning')
            end_date_str = None

    if department_id:
        dept_exists = Department.query.get(department_id)
        if dept_exists:
            query = query.filter(Event.department_id == department_id)
        else:
            flash(f'Department ID {department_id} not found.', 'warning')
            department_id = None

    if category: # Filter by category if provided
         query = query.filter(Event.category == category)

    # --- Apply Sorting ---
    if sort_by == 'title':
        order_column = Event.title
    elif sort_by == 'category':
        order_column = Event.category
    elif sort_by == 'department':
        query = query.outerjoin(Department) # Join needed for sorting
        order_column = Department.name
    else: # Default to sorting by event date
        sort_by = 'date'
        order_column = Event.event_date

    # Apply sort order
    if sort_order == 'desc':
        query = query.order_by(desc(order_column))
    else:
        sort_order = 'asc' # Default to asc if invalid value
        query = query.order_by(asc(order_column))

    # --- Pagination ---
    page = request.args.get('page', 1, type=int)
    try:
        pagination = query.paginate(page=page, per_page=10, error_out=False)
    except Exception as e:
        flash(f'Error retrieving events: {e}', 'danger')
        pagination = None
        events = []
    if pagination:
        events = pagination.items
    else:
        events = []

    # --- Get Data for Filter Form ---
    departments = Department.query.order_by(Department.name).all() if pagination else []
    # Get distinct categories currently used in events (or use predefined list)
    # Option 1: Query distinct categories from DB (might be slow on large tables)
    # categories = db.session.query(Event.category).distinct().order_by(Event.category).all()
    # categories = [cat[0] for cat in categories if cat[0]] # Extract string from tuple
    # Option 2: Use the predefined list from EventForm (simpler)
    event_form_categories = EventForm.category.kwargs.get('choices', [])
    categories = [choice[0] for choice in event_form_categories if choice[0]] # Get values, skip placeholder

    # --- Store current filters and sorting ---
    current_params = {
        'department_id': department_id if department_id is not None else 0,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'category': category, # Add category
        'sort_by': sort_by,
        'sort_order': sort_order
    }

    return render_template(
        'event_list.html',
        title='Events',
        events=events,
        pagination=pagination,
        departments=departments,
        categories=categories, # Pass categories for filter dropdown
        current_params=current_params
    )

# Route -> /events/123
@event_bp.route('/<int:event_id>')
@login_required
def event_detail(event_id):
    """Displays the details of a single event."""
    event = Event.query.get_or_404(event_id)
    return render_template('event_detail.html', title=event.title, event=event)

# Route -> /events/new
@event_bp.route('/new', methods=['GET', 'POST'])
@login_required
@publisher_required # Only publishers or admins can create
def event_create():
    """Handles creation of a new event."""
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            event_date=form.event_date.data,
            venue=form.venue.data,
            category=form.category.data,
            user_id=current_user.id # Set the organizer to the current user
        )
        if form.department_id.data and form.department_id.data > 0:
            event.department_id = form.department_id.data
        else:
            event.department_id = None

        db.session.add(event)
        db.session.commit()
        flash('Your event has been posted!', 'success')
        return redirect(url_for('event.event_list')) # Use namespaced endpoint

    return render_template('event_form.html', title='Post New Event', form=form, legend='New Event')

# Route -> /events/123/edit
@event_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def event_edit(event_id):
    """Handles editing an existing event."""
    event = Event.query.get_or_404(event_id)

    # Permission Check
    if not current_user.is_admin() and event.user_id != current_user.id:
        abort(403)

    form = EventForm(obj=event) # Pre-populate form on GET

    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.event_date = form.event_date.data
        event.venue = form.venue.data
        event.category = form.category.data
        if form.department_id.data and form.department_id.data > 0:
            event.department_id = form.department_id.data
        else:
            event.department_id = None

        # Track Edit
        event.last_edited_by_id = current_user.id

        db.session.commit()
        flash('Your event has been updated!', 'success')
        return redirect(url_for('event.event_detail', event_id=event.id)) # Use namespaced endpoint

    return render_template('event_form.html', title='Edit Event', form=form, legend='Edit Event')

# Route -> /events/123/delete
@event_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def event_delete(event_id):
    """Handles deleting an event."""
    event = Event.query.get_or_404(event_id)

    # Permission Check
    if not current_user.is_admin() and event.user_id != current_user.id:
        abort(403)

    # Cascade delete should handle associated MediaFiles automatically

    db.session.delete(event)
    db.session.commit()
    flash('Event has been deleted!', 'success')
    return redirect(url_for('event.event_list')) # Use namespaced endpoint
