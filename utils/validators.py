import re
from email_validator import validate_email, EmailNotValidError


def validate_signup(username, email, password):
    if not username or len(username) < 3:
        return "Username must be at least 3 characters."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return "Username can only contain letters, numbers, and underscores."
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return "Invalid email address."
    if len(password) < 6:
        return "Password must be at least 6 characters."
    return None


def validate_login(email, password):
    if not email or not password:
        return "Email and password are required."
    return None


def validate_question(question):
    if not question:
        return "Question cannot be empty."
    if len(question) > 2000:
        return "Question too long (max 2000 characters)."
    return None
