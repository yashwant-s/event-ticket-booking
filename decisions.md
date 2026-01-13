# Design Decisions

## 1. Database Structure
I focused on three main entities: **User**, **Ticket**, and **Event**.
* **User:** I didn't create a specific table for this in the schema. Since authentication wasn't the main focus, I'm assuming we identify users via headers (which could be easily swapped for a JWT later).
* **Event & Ticket:** Standard one-to-many relationship. One event has many tickets.

### The "Ticket Pool" Strategy
The most important part of the schema is the `event_ticket_pools` table.
Instead of storing the total ticket count in a single row (e.g., inside the `Event` table), I split the inventory into multiple "pools" (e.g., partitions of 1000 tickets each).

**Why I did this:**
If we keep one global counter, every booking request has to lock that same specific row. This creates a "hot row" bottleneck where users end up waiting in a queue for the database lock. By splitting the inventory into multiple pools and having the code pick one randomly, we distribute the traffic and reduce locking contention significantly.

I also added an in-memory cache for static data (like ticket prices) to save on unnecessary DB reads.

---

## 2. Handling Race Conditions

### My Approach: Atomic Updates
Instead of locking a row, reading it, and then updating it, I used atomic SQL updates:
`UPDATE event_ticket_pools SET count = count - 1 WHERE id = ? AND count > 0`

If the update affects 0 rows (because the pool is empty), the code simply retries with a different pool.

### Rejected Alternatives

**1. Pessimistic Locking (`SELECT FOR UPDATE`)**
I considered locking the row explicitly, reading the value, and then writing it back. I rejected this because it holds the database connection open for too long. If we have high traffic, requests would pile up waiting for locks to release, killing throughput.

**2. Centralized Cache (Redis)**
I considered moving the inventory counter entirely to Redis.
* **Pros:** Redis is much faster (in-memory) than MySQL (disk).
* **Cons:** It introduces complexity. We'd have to manage distributed consistency (what if Redis updates but the DB write fails?).
* **Verdict:** For this implementation, I decided the complexity overhead wasn't worth it. The "Sharded SQL" approach is a happy medium that keeps the architecture simple but still performant.

---

## 3. Bottlenecks at Scale (1 Million RPS)

To be honest, the current SQL-based solution would struggle at 1 million requests per second.

**The Main Bottlenecks:**
1.  **Retry Storms:** As the event sells out, pools become empty. The code might have to check Pool A, then Pool B, then Pool C before finding a seat. This multiplies the number of queries just as the database is under the heaviest load.
2.  **Connection Limits:** Even with sharding, a relational database can only handle a few thousand active connections. 1 million RPS would exhaust the connection pool immediately.

**How I would fix it for that scale:**
I would move the inventory management entirely to a **Redis Cluster**. Redis can handle that level of throughput easily. We would decrement counters in Redis to give the user an immediate response, and then use a queue (like Kafka) to asynchronously sync the bookings to the SQL database for permanent storage.