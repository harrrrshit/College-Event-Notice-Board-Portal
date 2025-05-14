from flask import Blueprint, render_template
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('landing.html')
    # Show 5 most recent notices and 5 upcoming events
    from models import Notice, Event
    from datetime import datetime
    recent_notices = Notice.query.order_by(Notice.issue_date.desc()).limit(5).all()
    upcoming_events = Event.query.filter(Event.event_date >= datetime.now()).order_by(Event.event_date.asc()).limit(5).all()
    return render_template(
        'index.html',
        recent_notices=recent_notices,
        upcoming_events=upcoming_events
    )

# Add other main/static routes here later if needed (e.g., about page)
