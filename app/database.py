from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

#Single SQLAlchemy engine shared in the app. pool_pre_ping=True to handle stale DB sessions
#settings.DATABASE_URL in production
engine = create_engine(settings.TEST_DATABASE_URL, pool_pre_ping=True)

#Each request get its own DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#All our ORM models inherit from Base, giving SQLAlchemy the metadata it needs to generate tables.
Base = declarative_base()

def get_db():
    """
    The FastAPI dependency for providing a scoped database session.
    Ensures that the session is closed after request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()