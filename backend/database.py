import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env in project root
dotenv_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(dotenv_path=dotenv_path)

logger = logging.getLogger("joblens.database")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "job_map")

    if user and password:
        DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    else:
        default_db_file = os.path.join(PROJECT_ROOT, "joblens.db").replace("\\", "/")
        DATABASE_URL = f"sqlite:///{default_db_file}"
        logger.info("DATABASE_URL not set. Defaulting to local SQLite: %s", DATABASE_URL)

# Normalize relative SQLite path to PROJECT_ROOT
if DATABASE_URL.startswith("sqlite:///") and not (len(DATABASE_URL) > 11 and DATABASE_URL[11] == ":"):
    rel_path = DATABASE_URL[len("sqlite:///"):]
    abs_path = os.path.normpath(os.path.join(PROJECT_ROOT, rel_path)).replace("\\", "/")
    DATABASE_URL = f"sqlite:///{abs_path}"

connect_args = {}
engine_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    connect_args["timeout"] = 30.0  # Wait up to 30s during concurrent transactions
else:
    # Production PostgreSQL connection pooling
    engine_kwargs["pool_size"] = int(os.getenv("DB_POOL_SIZE", "20"))
    engine_kwargs["max_overflow"] = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 3600

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

# Enable WAL (Write-Ahead Logging) for SQLite for high-concurrency read/write
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def init_db():
    """Initializes database schema creating any missing tables."""
    Base.metadata.create_all(bind=engine)
