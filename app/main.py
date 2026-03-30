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

app = FastAPI()

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
