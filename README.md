# Transaction Rate Limiter API

## 1. What This Is
A backend portfolio project demonstrating a robust API rate limiter. It uses a **sliding window algorithm** backed by Redis to restrict the number of transactions a user can perform within a given timeframe. If a user exceeds their quota, they receive a `429 Too Many Requests` response.

## 2. Architecture
- **Web Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Stores users and credentials)
- **Cache / Rate Limiter**: Redis (Stores rate-limit counts using Sorted Sets)
- **Auth**: JWT (JSON Web Tokens) with bcrypt password hashing
- **Infrastructure**: Docker & Docker Compose (Local), Railway (Production)

## 3. Design Decisions
- **Sliding Window vs Token Bucket**: Chosen sliding window using Redis `ZSET` to allow for highly accurate, millisecond-level precision of request throttling without the burst problems associated with fixed-window counters.
- **Redis Pipelines**: Used Redis pipelines for the rate limiting operations (ZREMRANGEBYSCORE, ZADD, ZCARD, EXPIRE) to batch commands and minimize network roundtrips, ensuring atomic operations and high performance.
- **Dependency Injection**: Used FastAPI's `Depends` for extracting the JWT token and current user ID, making the code modular and easily testable.

## 4. Load Test Results
*(To be populated after deployment load tests)*

## 5. How To Run
### Prerequisites
- Docker & Docker Compose
- Python 3.10+

### Setup
1. Clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Start the infrastructure (PostgreSQL & Redis):
   ```bash
   docker compose up -d
   ```
4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## 6. Endpoints
- `POST /auth/register`: Register a new user.
- `POST /auth/login`: Authenticate and receive a JWT.
- `GET /protected`: Test JWT authentication.
- `POST /transactions`: Mock transaction endpoint (Rate Limited to 5 requests / 60 seconds).
- `GET /ratelimit/status`: Check remaining quota without triggering a limit increment.
- `GET /metrics`: Health and application metrics.
