# Python / Flask Secure Support Ticket Portal

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Additional Resources](#additional-resources)

## Overview

This **Support Ticket System** is an internal tool developed to streamline client support and issue resolution. This system allows clients to log in securely, submit support tickets and monitor the status of their requests. 

Users with the "administrator" role can view, manage and respond to all submitted tickets. They can also view and manage client user accounts and view failed login attempts

## Features

- **Secure Login**: Users can log in with cryptographically secure password storage, using a combination of salting, peppering and hashing to protect passwords.
- **Two-Factor Authentication (2FA)**: App-based 2FA provides an extra layer of security for user logins.
- **Account Registration with Email Verification**: New users can register and verify their account via email using the Mailgun API.
- **Cross-Site Request Forgery (CSRF) Protection**: CSRF tokens are implemented to prevent unauthorized commands from external sources.
- **IP-Based Rate Limiting**: Protects the login form from brute-force attacks by limiting login attempts from the same IP address.
- **Input Sanitization and Prepared Statements**: Ensures protection against SQL injection and invalid input handling.
- **Output Escaping**: Mitigates cross-site scripting (XSS) vulnerabilities by escaping user-generated output.
- **Enforced HTTPS in Production**: All communications in the production environment are forced to use HTTPS for secure data transfer.
- **Obscured Error Messages**: Non-specific error messages on failed login attempts help prevent user enumeration.
- **User-Friendly Interface**: An intuitive UI allows for easy navigation, making it simple for clients to place tickets and staff to manage them.

## Installation

1. **Clone the repository**:
   ```bash
   git clone git@github.com:dhedley9/python-flask-support-ticket-portal.git
   ```

2. **Navigate to the project directory**:
    ```bash
    cd python-flask-support-ticket-portal
    ```

3. **Create a virtual environment** (recommended):
    ```bash
    python3 -m venv venv       # On Windows, use `python -m venv venv`
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

4. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Set up environment file**:

    In the root directory create a .env file by copying the .env.example file

    ```bash
    cp .env.example .env
    ```

6. **Replace environment secrets**:

    Once you have created your .env file you will need to replace the following environment variables with secure keys:

    - SECRET_KEY
    - PEPPER

    You can create a strong random key using Python:

    ```python
    import secrets
    print(secrets.token_hex(32))
    ```

7. **Replace credentials for the default admin user**:

    As part of the initial setup, the app will automatically create an admin user for you. Change the default credentials for this user using the environment variables below, you can also change the login credentials later within the app:

    - DEFAULT_USER
    - DEFAULT_PASSWORDS

8. **Replace Mailgun credentials**:

    The application uses Mailgun to provide email sending functionality. The app uses the Mailgun API to add this functionality and requires the following environment variables to be configured. For more information on how to setup Mailgun, see the [Additional Resources](#additional-resources)

    - MAILGUN_API_KEY - the Mailgun API key created for the application
    - MAILGUN_DOMAIN - the sending domain used for Mailgun (Mailgun recommends this to be a subdomain, e.g. mailgun.example.com)
    - MAILGUN_DOMAIN_REGION - the region the sending domain is hosted on Mailgun, by default this is "us" but can also be "eu"

9. **Run the application**:

    ```bash
    flask run
    ```

## Additional Resources

TODO