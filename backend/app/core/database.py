from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create engine - PostgreSQL doesn't need check_same_thread
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=20,  # Increased from 5 to handle more concurrent requests
    max_overflow=30,  # Increased from 10 to prevent connection exhaustion
    pool_recycle=3600  # Recycle connections after 1 hour to prevent stale connections
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
