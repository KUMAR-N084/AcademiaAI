import pytest
from app import create_app, mongo
from config import TestConfig
from models.user import User
from pymongo.errors import DuplicateKeyError


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        mongo.db.users.delete_many({})
        mongo.db.history.delete_many({})
    yield app
    with app.app_context():
        mongo.db.users.delete_many({})
        mongo.db.history.delete_many({})


@pytest.fixture
def client(app):
    return app.test_client()


def test_signup_page(client):
    res = client.get("/signup")
    assert res.status_code == 200
    assert b"Create Account" in res.data


def test_login_page(client):
    res = client.get("/login")
    assert res.status_code == 200
    assert b"Welcome back" in res.data


def test_signup_success(client):
    res = client.post("/signup", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }, follow_redirects=True)
    assert res.status_code == 200


def test_signup_short_username(client):
    res = client.post("/signup", data={
        "username": "ab",
        "email": "a@b.com",
        "password": "testpass"
    })
    assert b"at least 3 characters" in res.data


def test_login_invalid(client):
    res = client.post("/login", data={
        "email": "nouser@example.com",
        "password": "wrong"
    })
    assert b"Invalid email or password" in res.data


def test_protected_route_redirects(client):
    res = client.get("/", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.location


def test_logout_requires_post(client):
    res = client.get("/logout")
    assert res.status_code == 405


def test_user_email_uniqueness_enforced(app):
    with app.app_context():
        User.create("userone", "duplicate@example.com", "password123")
        with pytest.raises(DuplicateKeyError):
            User.create("usertwo", "duplicate@example.com", "password456")
