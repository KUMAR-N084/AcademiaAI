from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from pymongo.errors import DuplicateKeyError
from utils.validators import validate_signup, validate_login
import logging

auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        error = validate_signup(username, email, password)
        if error:
            flash(error, "error")
            return render_template("signup.html")

        if User.get_by_email(email):
            flash("Email already registered.", "error")
            return render_template("signup.html")

        if User.get_by_username(username):
            flash("Username already taken.", "error")
            return render_template("signup.html")

        try:
            user = User.create(username, email, password)
            login_user(user)
            flash("Welcome! Account created successfully.", "success")
            return redirect(url_for("main.index"))
        except DuplicateKeyError:
            flash("Email or username is already registered.", "error")
        except Exception as e:
            logger.error(f"Signup error: {e}")
            flash("Something went wrong. Please try again.", "error")

    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        error = validate_login(email, password)
        if error:
            flash(error, "error")
            return render_template("login.html")

        user = User.get_by_email(email)
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        login_user(user)
        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))
