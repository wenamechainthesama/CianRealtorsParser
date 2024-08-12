from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, RealtorId, RealtorData
from ...config import DATABASE_URL

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

__all__ = ["RealtorId", "RealtorData", "Base", "session"]
