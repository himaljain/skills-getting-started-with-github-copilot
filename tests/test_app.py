import copy
from fastapi.testclient import TestClient

import src.app as app_module


client = TestClient(app_module.app)


def setup_function():
    # keep a deep copy of activities so tests can modify safely
    setup_function._activities_backup = copy.deepcopy(app_module.activities)


def teardown_function():
    # restore original activities
    app_module.activities.clear()
    app_module.activities.update(setup_function._activities_backup)


def test_get_activities_structure():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Check some known activity exists
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser@example.com"

    # ensure email not present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # now present
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # unregister
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # now absent
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_signup_duplicate_fails():
    activity = "Chess Club"
    # take an existing participant
    existing = app_module.activities[activity]["participants"][0]
    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_nonexistent_fails():
    activity = "Chess Club"
    email = "not-registered@example.com"
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 400
