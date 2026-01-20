"""Tests for the FastAPI activities endpoints"""
import pytest


def test_get_activities(client, reset_activities):
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data) == 9


def test_get_activities_chess_club_details(client, reset_activities):
    """Test that Chess Club activity has correct structure"""
    response = client.get("/activities")
    data = response.json()
    
    chess_club = data["Chess Club"]
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert chess_club["max_participants"] == 12
    assert len(chess_club["participants"]) == 2
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


def test_signup_new_participant(client, reset_activities):
    """Test signing up a new participant for an activity"""
    response = client.post(
        "/activities/Basketball%20Team/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up newstudent@mergington.edu for Basketball Team"
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" in activities["Basketball Team"]["participants"]


def test_signup_duplicate_participant(client, reset_activities):
    """Test that signing up a duplicate participant fails"""
    # Try to sign up someone already registered
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client, reset_activities):
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_participant(client, reset_activities):
    """Test unregistering a participant from an activity"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert len(activities["Chess Club"]["participants"]) == 1


def test_unregister_nonexistent_participant(client, reset_activities):
    """Test unregistering a participant not in the activity"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"]


def test_unregister_from_nonexistent_activity(client, reset_activities):
    """Test unregistering from a non-existent activity"""
    response = client.delete(
        "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_and_unregister_workflow(client, reset_activities):
    """Test the complete workflow of signing up and then unregistering"""
    email = "testworkflow@mergington.edu"
    activity = "Swimming Club"
    
    # Sign up
    signup_response = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    assert signup_response.status_code == 200
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity]["participants"]
    
    # Unregister
    unregister_response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    assert unregister_response.status_code == 200
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity]["participants"]
