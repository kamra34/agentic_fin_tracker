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
    pool_recycle=3600,  # Recycle connections after 1 hour to prevent stale connections
    connect_args={
        # Safety net for LEAKED transactions: if a connection is left open *inside a
        # transaction* and idle (no statement running) for this long, PostgreSQL
        # terminates that backend so it can't hold locks / a pool slot indefinitely.
        # NOTE: this GUC is set on every physical connection in the pool, and
        # readonly_engine below shares the SAME pool, so it applies pool-wide. On a
        # normal transactional session it fires on ANY transaction left idle this long
        # (not only "leaked" ones), so the window is deliberately generous (5 min) to
        # avoid killing merely-slow request transactions. AUTOCOMMIT connections
        # (readonly_engine) never sit in a transaction, so they're unaffected.
        "options": "-c idle_in_transaction_session_timeout=300000",
    },
)

# Read-only variant of the engine: every statement runs in AUTOCOMMIT, so a SELECT
# is committed immediately and NO transaction is held between statements. This shares
# the SAME connection pool as `engine` (only the isolation level differs). Use it for
# request paths that only read and interleave long external calls - e.g. the
# multi-agent chat flow, which calls OpenAI/market-data APIs between DB reads. Without
# it, the first SELECT opens a transaction that stays "idle in transaction" (holding
# AccessShareLocks) for the entire duration of those external calls.
readonly_engine = engine.execution_options(isolation_level="AUTOCOMMIT")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ReadOnlySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=readonly_engine)

Base = declarative_base()


def get_db():
    """Transactional session for read/write request paths."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # Make sure a failed request rolls back before the connection is returned
        # to the pool, so no half-open transaction lingers.
        db.rollback()
        raise
    finally:
        db.close()


def get_readonly_db():
    """AUTOCOMMIT session for READ-ONLY request paths.

    Because the underlying connection runs in AUTOCOMMIT mode, each SELECT commits
    immediately and no transaction is held open between statements. This prevents
    'idle in transaction' build-up when a request interleaves DB reads with long
    external calls (OpenAI, market-data APIs, etc.) - see the chat/agents flow.

    WARNING: the read-only contract is by convention only, not enforced. Any write
    (INSERT/UPDATE/DELETE) issued on this session is COMMITTED THE INSTANT it executes
    and CANNOT be rolled back - a mid-request error would leave a partial, irreversible
    write. This function deliberately does NOT roll back on error (there is nothing to
    roll back under AUTOCOMMIT). Only use it for paths that exclusively read; if a write
    is ever needed, depend on get_db (transactional) instead.
    """
    db = ReadOnlySessionLocal()
    try:
        yield db
    finally:
        db.close()
