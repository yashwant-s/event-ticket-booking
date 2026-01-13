# 🎟️ Event Ticket Booking API

A robust, concurrent ticket booking system built with **FastAPI**, **MySQL**, and **Docker**.

## 🚀 Quick Start

### 1. Configuration
Create a `.env` file in the root directory:
```env
DB_HOST=db
DB_PORT=3306
DB_USERNAME=eventuser
DB_PASSWORD=eventpass123
DB_NAME=event
DB_ROOT_PASSWORD=rootpassword
DEBUG=True
```

### 2. Run the App
One command to start the Database and the API:
```bash
docker-compose up -d
```
API will be running at: **[http://localhost:8000/docs](http://localhost:8000/docs)**

### 2. Run Tests
Verify functionality with the End-to-End test suite:
```bash
# Install test tools
pip install pytest httpx

# Run tests
pytest tests/ -v
```

### 3. API Examples (Curl)

**Create Event**
```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "X-User-Id: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Concert 2025",
    "address": "Stadium",
    "event_time": "2026-06-01T20:00:00Z",
    "pool_size": 100,
    "ticket_price": 50.0
  }'
```

**Book Ticket**
```bash
curl -X POST http://localhost:8000/api/v1/tickets \
  -H "X-User-Id: 101" \
  -H "Content-Type: application/json" \
  -d '{"event_id": 1, "ticket_count": 2}'
```

**Cancel Ticket**
```bash
# Replace 1 with your actual ticket_id
curl -X DELETE http://localhost:8000/api/v1/tickets/1 \
  -H "X-User-Id: 101"
```

## 🛠️ Tech Stack
*   **Framework:** FastAPI (Python 3.12)
*   **Database:** MySQL 8.0
*   **Migrations:** Alembic
*   **Deployment:** Docker Compose

## 🔑 Key Features
*   **Concurrency Safe:** Handles concurrent booking requests using atomic database updates.
*   **Quota Management:** Enforces a hard limit of **2 tickets per user**.
*   **Scalable Architecture:** Extensible `event_ticket_pools` design (see [decisions.md](decisions.md)).
