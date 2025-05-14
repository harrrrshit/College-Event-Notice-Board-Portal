|.
|   .gitignore
|   app.py
|   config.py
|   config.py.example
|   decorators.py
|   forms.py
|   LICENSE
|   models.py
|   README.md
|   requirements.txt
|   wsgi.py
|
+---instance
|       college_board.db
|
+---migrations
|   |   alembic.ini
|   |   env.py
|   |   README
|   |   script.py.mako
|   |
|   \---versions
|       |   1f335732472f_initial_database_setup_with_all_models.py
|       |   c53c2cab1354_add_last_editor_tracking_to_notice_and_.py
|
+---routes
|   |   auth.py
|   |   events.py
|   |   main.py
|   |   notices.py
|   |   __init__.py
|
+---templates
|   |   base.html
|   |   event_detail.html
|   |   event_form.html
|   |   event_list.html
|   |   index.html
|   |   login.html
|   |   notice_detail.html
|   |   notice_form.html
|   |   notice_list.html
|   |   register.html
|   |
|   \---errors
|           403.html
|           404.html
|           500.html
