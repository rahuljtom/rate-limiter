from fastapi import FastAPI, HTTPException,Depends
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.middleware.auth_middleware import get_current_user
from dotenv import load_dotenv
load_dotenv()

# CREATE TABLES
Base.metadata.create_all(bind=engine)

from fastapi.responses import JSONResponse
from app.services.rate_limiter import check_rate_limit, get_rate_limit_status, RateLimitExceeded

app = FastAPI()

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too Many Requests. Rate limit exceeded."}
    )
# -------------------------
# AUTH: REGISTER
# -------------------------
@app.post("/auth/register")
def register(user: UserCreate):
    db = SessionLocal()

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)

    new_user = User(
        email=user.email,
        hashed_password=hashed
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}

# -------------------------
# AUTH: LOGIN
# -------------------------
@app.post("/auth/login")
def login(user: UserLogin):
    db = SessionLocal()

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(db_user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/protected")
def protected(user_id: str = Depends(get_current_user)):
    return {
        "message": "Access granted",
        "user_id": user_id
    }

# -------------------------
# TRANSACTIONS (Rate Limited)
# -------------------------
@app.post("/transactions")
def create_transaction(user_id: str = Depends(get_current_user)):
    # 1. Check rate limit (e.g., 5 requests per 60 seconds)
    limit_info = check_rate_limit(user_id, limit=5, window_seconds=60)
    
    # 2. Process transaction (mocked)
    return {
        "message": "Transaction created successfully",
        "transaction_id": "txn_12345",
        "rate_limit": limit_info
    }

# -------------------------
# RATE LIMIT STATUS
# -------------------------
@app.get("/ratelimit/status")
def rate_limit_status(user_id: str = Depends(get_current_user)):
    status = get_rate_limit_status(user_id, limit=5, window_seconds=60)
    return status

# -------------------------
# METRICS
# -------------------------
@app.get("/metrics")
def get_metrics():
    # Placeholder for demo metrics
    return {
        "status": "healthy",
        "active_users": 42,
        "total_transactions": 1024
    }
