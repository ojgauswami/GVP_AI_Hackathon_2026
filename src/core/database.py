from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import os

# Use SQLite by default for development if PostgreSQL is not available
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///gvp_phase1.db")

engine = create_engine(DATABASE_URL, echo=False)
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(session_factory)

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import core.models
    Base.metadata.create_all(bind=engine)
