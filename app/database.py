import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

raw_db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5434/ratelimiter")

if raw_db_url.startswith("postgres://"):
    DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://", 1)
else:
    DATABASE_URL = raw_db_url

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
