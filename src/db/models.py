from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class RealtorId(Base):
    __tablename__ = "realtors_id"

    id = Column(Integer, primary_key=True)
    data = relationship("RealtorData", uselist=False)


class RealtorData(Base):
    __tablename__ = "realtors_data"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    phone = Column(String(20), unique=True)
    realtor_id = Column(Integer, ForeignKey("realtors_id.id"))
