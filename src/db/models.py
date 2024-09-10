from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class RealtorId(Base):
    __tablename__ = "realtors_id"

    id = Column(Integer, primary_key=True, unique=True)
    already_used = Column(Boolean, default=False)
    data = relationship("RealtorData", uselist=False)


class RealtorData(Base):
    __tablename__ = "realtors_data"

    realtor_id = Column(
        Integer, ForeignKey("realtors_id.id"), primary_key=True, unique=True
    )
    name = Column(String(50))
    phone_number = Column(String(20))
    email = Column(String(100))
