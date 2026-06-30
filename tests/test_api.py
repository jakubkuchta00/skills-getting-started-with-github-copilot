import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    # Arrange: reset the in-memory activity store to a known baseline for each test.
    activities.clear()
    activities.update(
        {
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu"],
            }
        }
    )

    with TestClient(app) as test_client:
        yield test_client


def test_signup_adds_participant(client):
    # Arrange: choose an activity and a new email address.
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: sign up the new student through the API.
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: the response is successful and the participant was added.
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange: use an email that is already registered for the activity.
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act: try to sign up the same student twice.
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: the duplicate signup is rejected with a 400 response.
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activities[activity_name]["participants"].count(email) == 1


def test_unregister_removes_participant(client):
    # Arrange: select a participant that is currently enrolled.
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act: unregister the participant via the API.
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert: the removal succeeds and the participant is no longer listed.
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]
