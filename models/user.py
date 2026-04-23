from extensions import mongo
from flask_login import UserMixin
from bson.objectid import ObjectId
import bcrypt
from datetime import datetime, UTC


class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc["_id"])
        self.username = user_doc["username"]
        self.email = user_doc["email"]
        self.password_hash = user_doc["password_hash"]
        self.created_at = user_doc.get("created_at")

    @staticmethod
    def create(username, email, password):
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        )
        doc = {
            "username": username,
            "email": email.lower(),
            "password_hash": password_hash,
            "created_at": datetime.now(UTC)
        }
        result = mongo.db.users.insert_one(doc)
        doc["_id"] = result.inserted_id
        return User(doc)

    @staticmethod
    def ensure_indexes():
        mongo.db.users.create_index("email", unique=True)
        mongo.db.users.create_index("username", unique=True)

    @staticmethod
    def get_by_id(user_id):
        try:
            doc = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            return User(doc) if doc else None
        except Exception:
            return None

    @staticmethod
    def get_by_email(email):
        doc = mongo.db.users.find_one({"email": email.lower()})
        return User(doc) if doc else None

    @staticmethod
    def get_by_username(username):
        doc = mongo.db.users.find_one({"username": username})
        return User(doc) if doc else None

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash)
