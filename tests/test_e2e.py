import pytest
from datetime import datetime, timedelta, timezone
import uuid

def generate_unique_event_data():
    """Helper to generate unique event data for each test"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"Test Event {unique_id}",
        "address": f"123 Test St {unique_id}",
        "event_time": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "pool_size": 10,
        "ticket_price": 50.0
    }

def test_health_check():
    """Verify the API is reachable"""
    import httpx
    response = httpx.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json()["success"] == "true"

def test_create_event_success(client):
    """Test creating a new event"""
    data = generate_unique_event_data()
    response = client.post("/events", json=data, headers={"X-User-Id": "1"})
    
    assert response.status_code == 200
    result = response.json()["data"]
    assert result["event_name"] == data["name"]
    assert "event_id" in result
    return result["event_id"]

def test_book_ticket_success(client):
    """Test booking tickets successfully"""
    # 1. Create Event
    event_id = test_create_event_success(client)
    
    # 2. Book Tickets
    booking_payload = {
        "event_id": event_id,
        "ticket_count": 2
    }
    response = client.post("/tickets", json=booking_payload, headers={"X-User-Id": "100"})
    
    assert response.status_code == 200
    result = response.json()["data"]
    assert result["status"] == "booked"
    assert result["ticket_count"] == 2
    assert result["event_id"] == event_id

def test_book_ticket_limit_exceeded(client):
    """Test user cannot exceed max tickets per event"""
    # 1. Create Event
    event_id = test_create_event_success(client)
    
    # 2. Book 2 Tickets (Limit is 2) - Should Success
    client.post("/tickets", json={"event_id": event_id, "ticket_count": 2}, headers={"X-User-Id": "101"})
    
    # 3. Try to Book 1 more - Should Fail
    response = client.post("/tickets", json={"event_id": event_id, "ticket_count": 1}, headers={"X-User-Id": "101"})
    
    assert response.status_code == 400
    assert "Ticket quota" in response.json()["message"]

def test_event_sold_out(client):
    """Test booking fails when event is sold out"""
    # 1. Create Event with small pool
    data = generate_unique_event_data()
    data["pool_size"] = 2  # Only 2 tickets available
    response = client.post("/events", json=data, headers={"X-User-Id": "1"})
    event_id = response.json()["data"]["event_id"]
    
    # 2. User A buys 2 tickets -> Pool Empty
    response = client.post("/tickets", json={"event_id": event_id, "ticket_count": 2}, headers={"X-User-Id": "201"})
    assert response.status_code == 200
    
    # 3. User B tries to buy 1 ticket -> Should Fail (Sold Out) because get_pools_with_tickets returns empty list
    response = client.post("/tickets", json={"event_id": event_id, "ticket_count": 1}, headers={"X-User-Id": "202"})
    
    assert response.status_code == 404
    assert "sold out" in response.json()["message"]

def test_cancel_ticket_restores_pool(client):
    """Test cancelling a ticket makes it available again"""
    # 1. Create Event with only 1 ticket
    data = generate_unique_event_data()
    data["pool_size"] = 1
    response = client.post("/events", json=data, headers={"X-User-Id": "1"})
    event_id = response.json()["data"]["event_id"]
    
    # 2. User A buys the last ticket
    response = client.post("/tickets", json={"event_id": event_id, "ticket_count": 1}, headers={"X-User-Id": "301"})
    assert response.status_code == 200
    ticket_id = response.json()["data"]["ticket_id"]
    
    # 3. User B tries to buy -> Fails (Sold Out)
    response = client.post("/tickets", json={"event_id": event_id, "ticket_count": 1}, headers={"X-User-Id": "302"})
    assert response.status_code == 404
    
    # 4. User A cancels their ticket
    response = client.delete(f"/tickets/{ticket_id}", headers={"X-User-Id": "301"})
    assert response.status_code == 200
    
    # 5. User B tries to buy again -> Should Success now!
    response = client.post("/tickets", json={"event_id": event_id, "ticket_count": 1}, headers={"X-User-Id": "302"})
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "booked"

def test_cancel_unauthorized(client):
    """Test user cannot cancel someone else's ticket"""
    # 1. User A buys ticket
    event_id = test_create_event_success(client)
    response = client.post("/tickets", json={"event_id": event_id, "ticket_count": 1}, headers={"X-User-Id": "401"})
    ticket_id = response.json()["data"]["ticket_id"]
    
    # 2. User B tries to cancel it
    response = client.delete(f"/tickets/{ticket_id}", headers={"X-User-Id": "402"})
    
    assert response.status_code == 401
    assert "not allowed" in response.json()["message"]
