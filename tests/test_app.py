import copy

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity():
    # Arrange
    email = "new@student.com"
    url = "/activities/Chess%20Club/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_existing_student():
    # Arrange
    existing_email = "michael@mergington.edu"
    url = "/activities/Chess%20Club/signup"
    params = {"email": existing_email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_nonexistent_activity():
    # Arrange
    url = "/activities/Nonexistent/signup"
    params = {"email": "x@x.com"}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity():
    # Arrange
    email = "to_remove@student.com"
    signup_url = "/activities/Chess%20Club/signup"
    unregister_url = "/activities/Chess%20Club/unregister"
    signup_params = {"email": email}
    unregister_params = {"email": email}

    # Act
    signup_response = client.post(signup_url, params=signup_params)
    unregister_response = client.post(unregister_url, params=unregister_params)

    # Assert
    assert signup_response.status_code == 200
    assert unregister_response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_not_signed():
    # Arrange
    url = "/activities/Chess%20Club/unregister"
    params = {"email": "nobody@x.com"}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
