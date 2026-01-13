import concurrent.futures
import pytest
import httpx
import time

BASE_URL = "http://localhost:8000/api/v1"

def book_ticket(event_id, user_id):
    """
    Attempt to book 1 ticket for the given event.
    Returns status code.
    """
    url = f"{BASE_URL}/tickets"
    headers = {"X-User-Id": str(user_id)}
    payload = {
        "event_id": event_id,
        "ticket_count": 1
    }
    
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
        return response.status_code
    except httpx.ReadTimeout:
        return 504  # Gateway Timeout (simulated)
    except Exception as e:
        return 500

def test_race_condition_booking():
    """
    Simulate a race condition:
    - Create event with 10 tickets.
    - 20 users try to book simultaneously.
    - Expect exactly 10 successes (200 OK) and 10 failures (400 Bad Request / 404).
    """
    
    # 1. Create Event with 10 tickets
    admin_headers = {"X-User-Id": "1"}
    event_payload = {
        "name": "Race Condition Concert",
        "description": "Testing limits",
        "address": "Test Stadium",
        "event_time": "2026-06-01T20:00:00Z",
        "pool_size": 10,
        "ticket_price": 50.0
    }
    
    resp = httpx.post(f"{BASE_URL}/events", json=event_payload, headers=admin_headers)
    if resp.status_code != 200:
        print(f"Error creating event: {resp.status_code} - {resp.text}")
    assert resp.status_code == 200
    event_id = resp.json()["data"]["event_id"]
    print(f"\nCreated Event {event_id} with 10 tickets.")

    # 2. Launch 20 concurrent booking requests
    total_users = 20
    workers = 20
    
    # Use random User IDs to avoid 'Limit Exceeded' (2 per user) logic interfering
    # We want to test POOL limits, not USER limits.
    # So user_id will be unique for each request: 1000 to 1020
    user_ids = list(range(1000, 1000 + total_users))
    
    status_codes = []
    
    print(f"Launching {total_users} simultaneous requests...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(book_ticket, event_id, uid) for uid in user_ids]
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            status_codes.append(res)
            
    # 3. Analyze Results
    from collections import Counter
    counts = Counter(status_codes)
    print("\n--- Status Code Distribution ---")
    for code, count in counts.items():
        print(f"Status {code}: {count}")

    success_count = status_codes.count(200)
    failure_count_400 = status_codes.count(400) # Sold out / Error
    failure_count_404 = status_codes.count(404) # Sold out (explicit)
    failure_count_504 = status_codes.count(504) # Timeout
    failure_count_500 = status_codes.count(500) # Other error
    
    total_failures = failure_count_400 + failure_count_404 + failure_count_504 + failure_count_500
    
    print("\n--- Results ---")
    print(f"Total Requests: {total_users}")
    print(f"Successes (200): {success_count}")
    print(f"Failures (400/404/504): {total_failures}")
    
    # 4. Assertions
    # We must have EXACTLY 10 sales (since pool size was 10)
    assert success_count == 10, f"Expected 10 sold tickets, but sold {success_count}"
    
    # The rest should fail (gracefully or timeout)
    assert total_failures == 10, f"Expected 10 failures, but got {total_failures}"

if __name__ == "__main__":
    print(">>> Running Overselling Test (Pool Limit)")
    test_race_condition_booking()
    
    print("\n>>> Running User Limit Test (Max 2 Per User)")
    # New Test: One user trying to book 10 times
    # 1. Create Event with plenty of tickets (100)
    admin_headers = {"X-User-Id": "1"}
    event_payload = {
        "name": "User Limit Concert",
        "description": "Testing user limits",
        "address": "Stadium",
        "event_time": "2026-06-01T20:00:00Z",
        "pool_size": 100,
        "ticket_price": 50.0
    }
    
    resp = httpx.post(f"{BASE_URL}/events", json=event_payload, headers=admin_headers)
    assert resp.status_code == 200
    event_id = resp.json()["data"]["event_id"]
    
    # 2. Launch 10 concurrent requests for SAME User
    user_id = 9999
    workers = 10
    
    status_codes = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # distinct requests, but same user_id and event_id
        futures = [executor.submit(book_ticket, event_id, user_id) for _ in range(10)]
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            status_codes.append(res)
            
    success_count = status_codes.count(200)
    failures = len(status_codes) - success_count
    
    print(f"User {user_id} attempted 10 simultaneous bookings.")
    print(f"Successes: {success_count} (Allowed Max: 2)")
    print(f"Failures: {failures}")
    
    # We suspect this might FAIL (Success > 2) because we checked 'Limit' before 'Booking' without a lock.
    if success_count > 2:
        print("❌ RACE DETECTED: User exceeded limit!")
    else:
        print("✅ Limit enforced correctly.")
