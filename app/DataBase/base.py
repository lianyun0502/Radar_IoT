from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./app/Demo_IoT.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
    echo=True
)
SessionLocal:sessionmaker = sessionmaker(bind=engine)

Base = declarative_base()

#Dependency
def get_db():
    db:Session = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()