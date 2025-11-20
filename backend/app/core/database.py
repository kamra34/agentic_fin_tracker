from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import time

logger = logging.getLogger(__name__)

# Create engine - PostgreSQL doesn't need check_same_thread
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Add query timing for performance monitoring
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
    total_time = (time.time() - context._query_start_time) * 1000

    # Log slow queries (over 100ms)
    if total_time > 100:
        # Truncate long queries for readability
        query_preview = statement[:200] + "..." if len(statement) > 200 else statement
        query_preview = query_preview.replace('\n', ' ').strip()
        logger.warning(f"🐌 SLOW QUERY ({total_time:.2f}ms): {query_preview}")
    elif total_time > 50:
        query_preview = statement[:150] + "..." if len(statement) > 150 else statement
        query_preview = query_preview.replace('\n', ' ').strip()
        logger.info(f"⚡ QUERY ({total_time:.2f}ms): {query_preview}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
