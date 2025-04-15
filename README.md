# College Event & Notice Board Portal

## Description

This project is a Flask-based web application designed to serve as a centralized platform for a college community. It provides distinct sections for official announcements (Notices) and upcoming events, aiming to replace scattered communication methods with a reliable, accessible, and filterable source of information.

Built as a learning project, it demonstrates core web development principles including user authentication, role-based access control, database interactions (CRUD operations), form handling, and dynamic template rendering.

## Features

*   **User Authentication:** Secure user registration and login (supports username or email).
*   **Role-Based Access Control:**
    *   **Student:** View notices and events.
    *   **Publisher:** Create, edit, and delete their own notices and events.
    *   **Admin:** Full CRUD control over all notices/events, plus potential future user management capabilities.
*   **Notice Management:**
    *   Create, view, edit, and delete official notices.
    *   Markdown support for notice content rendering.
    *   Tracking of the last editor and edit timestamp.
*   **Event Management:**
    *   Create, view, edit, and delete upcoming events.
    *   Fields for date/time, venue, category, and description.
    *   Validation to prevent creating events in the past.
    *   Markdown support for event descriptions.
    *   Tracking of the last editor and edit timestamp.
*   **Filtering & Sorting:**
    *   Filter notice/event lists by Department, Date Range, and Category (for events).
    *   Sort notice/event lists by various criteria (Date, Title, Department, Category).
    *   Pagination for long lists.
*   **Structured Codebase:**
    *   Application Factory pattern (`create_app`).
    *   Blueprints for modular routing (main, auth, notices, events).
    *   Separated files for models (`models.py`), forms (`forms.py`), configuration (`config.py`), decorators (`decorators.py`), and routes (`routes/` package).
*   **User-Friendly Interface:**
    *   Uses Bootstrap 5 for styling and responsiveness.
    *   Custom error pages for 403, 404, 500 errors.
    *   Flashed messages for user feedback.

## Technology Stack

*   **Language:** Python 3.13
*   **Framework:** Flask
*   **Database:** SQLite
*   **ORM:** Flask-SQLAlchemy
*   **Migrations:** Flask-Migrate (using Alembic)
*   **Forms:** Flask-WTF (+ email-validator)
*   **Authentication:** Flask-Login, Werkzeug (password hashing `pbkdf2:sha256`)
*   **Markdown Rendering:** Flask-Misaka
*   **Frontend:** HTML, Jinja2 Templates, Bootstrap 5 (via CDN)
*   **Version Control:** Git, GitLab

## Setup and Installation

Follow these steps to set up and run the project locally:

1.  **Prerequisites:**
    *   Python 3.13 or higher installed.
    *   Git installed.

2.  **Clone the Repository:**
    ```bash
    git clone https://gitlab.com/harrrrshit_k/college-event-notice-board-portal
    cd college-event-notice-board-portal/college_portal
    ```

3.  **Create and Activate Virtual Environment:**
    *   It's highly recommended to use a virtual environment.
    ```bash
    # Create the environment (use python3 if python maps to Python 2)
    python -m venv venv

    # Activate the environment
    # Windows (Git Bash or CMD/PowerShell might differ slightly):
    source venv/Scripts/activate
    # macOS / Linux:
    source venv/bin/activate
    ```
    *You should see `(venv)` at the beginning of your terminal prompt.*

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure the Application:**
    *   The application requires a configuration file named `config.py` in the `college_portal` directory. This file is ignored by Git for security.
    *   Copy the example configuration:
        ```bash
        # Windows
        copy config.py.example config.py
        # macOS / Linux
        cp config.py.example config.py
        ```
    *   **Generate a Secret Key:** Open `config.py` in a text editor. You need to replace the placeholder value for `SECRET_KEY` with a strong, random string. You can generate one using Python:
        ```bash
        # Run this in a separate python interpreter session
        python -c "import secrets; print(secrets.token_hex(24))"
        ```
        Copy the output and paste it as the value for `SECRET_KEY` in `config.py`.
    *   Verify `SQLALCHEMY_DATABASE_URI` points to the desired location (default is `instance/college_board.db` within the project folder).

6.  **Set Up the Database:**
    *   Apply the database migrations to create the necessary tables:
        ```bash
        flask db upgrade
        ```
    *   This will create the `instance/college_board.db` file if it doesn't exist.

7.  **Run the Application:**
    ```bash
    flask run
    ```
    *   The application should now be running on `http://127.0.0.1:5000` (or the address shown in your terminal).

## Usage

1.  **Access the Application:** Open your web browser and go to `http://127.0.0.1:5000`.
2.  **Register/Login:** Use the "Register" link to create an account (default role is 'student'). Use the "Login" link to sign in.
3.  **Roles:**
    *   **Admin/Publisher:** To create users with 'admin' or 'publisher' roles, you may need to manually create them or update their roles using `flask shell`:
        ```bash
        # Activate venv first
        flask shell
        >>> from app import db
        >>> from models import User
        # Find user
        >>> u = User.query.filter_by(username='your_username').first()
        # Change role
        >>> u.role = 'admin' # or 'publisher'
        # Save changes
        >>> db.session.commit()
        >>> exit()
        ```
    *   **Publishers/Admins** can use the "Post New Notice" and "Post New Event" buttons. They can edit/delete their own content.
    *   **Admins** can edit/delete *any* content.
4.  **Viewing:** Browse notices and events using the navigation links. Use the filter and sort options on the list pages.

## Future Work

This project provides a solid foundation for a college portal. Development is ongoing, with plans to incorporate additional advanced features and enhancements to further improve functionality and user experience based on community needs and feedback.

## Deployment

This application can potentially be deployed to platforms like PythonAnywhere. Key considerations for deployment include:

*   Setting `DEBUG = False` in production.
*   Managing the `SECRET_KEY` securely via environment variables on the hosting platform.
*   Configuring the database connection (SQLite might work on simple platforms, but PostgreSQL/MySQL are recommended for larger scale).
*   Using a production-grade WSGI server (like Gunicorn or uWSGI) instead of the Flask development server.

*(Placeholder: Live URL if deployed)*

## License

This project is licensed under the **PolyForm Noncommercial License 1.0.0**.

You may use, copy, modify, and distribute the software, but **only for noncommercial purposes**. You may not use the software for commercial purposes, including as part of a service or product you provide to others. Use by specific types of noncommercial organizations (educational, charitable, government, etc.) is permitted for noncommercial purposes.

Please see the [LICENSE](LICENSE) file for the full text of the license.

