# Support Ticket System - v1.0.0

## Summary
This application is a basic support ticket system built with Flask. Each ticket consists of a user-entered title and associated comments.

It has two tiers of user: 'Standard' and 'Administrator'

Standard users can:
- register
- login
- create tickets
- view their own tickets
- add comments (to their own tickets)
- mark their own tickets as resolved
- update their own account details

Administrator users can additionally:
- view all users
- edit other users
- delete users
- delete tickets
- view any ticket
- comment on any ticket
- mark any ticket as resolved
- delete tickets

When a ticket is updated by a standard user it will move into the status 'Awaiting Staff Reply' (active).
Conversely, when a ticket is updated by an admin user it will move into the status 'Awaiting Client Reply' (pending).

The entire portal is password protected except for the following routes:
- /login/
- /register/

Any route which requires login will automatically be redirected to /login/ if the current user is not logged in. 
The register route /register/ can be used to sign-up for a 'Standard' account.
Standard accounts can be promoted to 'Administrator' from an existing 'Administrator' account.

## Dependencies
The application uses several Flask extensions and libraries to provide a secure and user-friendly experience:

- **Bleach**: Used for sanitizing inputs to prevent injection attacks.
- **Flask-Login**: Handles user authentication, allowing users to log in and log out, and manages user sessions.
- **Flask-WTF**: Provides CSRF form protection to secure the application from cross-site request forgery attacks.

## Dependencies - Installation
To run this application, you will need to install the following dependencies:

- Flask
- Bleach
- Flask-Login
- Flask-WTF

You can install these dependencies using pip:

pip install flask bleach flask-login flask-wtf

## Tested With (versions)

- Python 3.12.0
- Flask 3.0.1
- Bleach 6.1.0
- Flask-Login 0.6.3
- Flask-WTF 1.2.1

## Usage
To use the application, first ensure that all dependencies are installed. Then, run the application using the Flask command:

flask run

## Logs

The application contains a logs directory which can be found in the /logs/ directory from the main app.py file, it contains the following log files:

- user-logins.log - records successful and failed login attempts

## Default configuration

The application will automatically run on an available network interface and port.
This can be found in the terminal when the application is run.
By default this will be http://127.0.0.1:5000/

On initial app startup, a default admin user will be created with the following credentials:

Email: admin@admin.co.uk
Password: password

These credentials can be changed upon login

## Application Structure

app.py - the main application file
/core/ - directory containing files and classes which provide core application functionality
/logs/ - logs directory
/sql/ - directory containing the sqlite database
/static/ - directory containing static assets (e.g. CSS)
/templates/ - contains template HTML files for portal pages