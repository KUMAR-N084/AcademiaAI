import pytest
from app import create_app, mongo
from config import TestConfig
from bson import ObjectId
from utils.validators import validate_question, validate_signup


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app


def test_validate_question_empty():
    assert validate_question("") == "Question cannot be empty."


def test_validate_question_long():
    assert "too long" in validate_question("x" * 2001).lower()


def test_validate_question_ok():
    assert validate_question("What is Python?") is None


def test_validate_signup_username():
    err = validate_signup("ab", "a@b.com", "password")
    assert "3 characters" in err


def test_validate_signup_email():
    err = validate_signup("abcd", "not-an-email", "password")
    assert "email" in err.lower()


def test_validate_signup_password():
    err = validate_signup("abcd", "a@b.com", "123")
    assert "6 characters" in err


def test_validate_signup_ok():
    assert validate_signup("abcd", "a@b.com", "password") is None


def test_video_requires_auth(app):
    client = app.test_client()
    res = client.post("/video", json={"topic": "python"})
    assert res.status_code in (302, 401)


def test_history_requires_auth_returns_json(app):
    client = app.test_client()
    res = client.get("/history")
    assert res.status_code == 401
    assert res.is_json
    assert "Authentication required" in res.get_json()["error"]


def test_video_encodes_topic(client):
    client.post("/signup", data={
        "username": "video_user",
        "email": "video@example.com",
        "password": "testpass123"
    }, follow_redirects=True)
    res = client.post("/video", json={"topic": "python & autoplay=1"})
    assert res.status_code == 200
    assert "%26" in res.get_json()["embed"]


def test_delete_history_returns_not_found_for_missing_item(client):
    client.post("/signup", data={
        "username": "history_user",
        "email": "history@example.com",
        "password": "testpass123"
    }, follow_redirects=True)
    res = client.delete(f"/history/{ObjectId()}")
    assert res.status_code == 404
    assert res.get_json() == {"success": False}
