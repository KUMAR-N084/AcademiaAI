from flask import Flask, flash, jsonify, redirect, request, url_for
import flask_pymongo
from config import Config
from extensions import csrf, mongo, login_manager
from flask_wtf.csrf import CSRFError
import logging


API_ENDPOINTS = {
    "main.ask",
    "main.visualize",
    "main.video",
    "main.history",
    "main.delete_history",
    "main.export_pdf",
}


def _is_api_request():
    return request.endpoint in API_ENDPOINTS


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Initialize extensions
    if app.config.get("MONGO_MOCK"):
        import mongomock

        original_client = flask_pymongo.MongoClient
        try:
            flask_pymongo.MongoClient = mongomock.MongoClient
            mongo.init_app(app)
        finally:
            flask_pymongo.MongoClient = original_client
    else:
        mongo.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    from models.user import User
    with app.app_context():
        User.ensure_indexes()

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    @login_manager.unauthorized_handler
    def unauthorized():
        if _is_api_request():
            return jsonify({"error": "Authentication required."}), 401
        return redirect(url_for("auth.login"))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Server error: {e}")
        return {"error": "Internal server error"}, 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        if _is_api_request():
            return jsonify({"error": "Session expired. Refresh the page and try again."}), 400
        flash("Session expired. Please try again.", "error")
        if request.endpoint == "auth.signup":
            return redirect(url_for("auth.signup"))
        return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config.get("DEBUG", False))
