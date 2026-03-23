import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore original participants before each test to ensure isolation."""
    originals = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, participants in originals.items():
        activities[name]["participants"] = participants


# --- GET /activities ---

def test_get_activities_returns_200():
    # Arrange (no setup needed)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200


def test_get_activities_contains_expected_activities():
    # Arrange
    expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
    # Act
    response = client.get("/activities")
    data = response.json()
    # Assert
    for activity in expected_activities:
        assert activity in data


def test_get_activities_has_required_fields():
    # Arrange (no setup needed)
    # Act
    response = client.get("/activities")
    data = response.json()
    # Assert
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


# --- DELETE /activities/{activity_name}/signup ---

def test_remove_participant_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_not_signed_up():
    # Arrange
    activity_name = "Chess Club"
    email = "ghost@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]


def test_remove_from_unknown_activity():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
