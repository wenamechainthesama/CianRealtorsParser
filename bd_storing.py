from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from realtors_links import RealtorParser


database_url = "sqlite:///C:\\Users\\Kirill\\Desktop\\CianRealtorsParser\\realtors.db"
engine = create_engine(database_url, echo=True)

Base = declarative_base()


class Realtor(Base):
    __tablename__ = "realtors"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    # name = Column(String(50), unique=True)
    # email = Column(String(100), unique=True)
    # phone = Column(String(20), unique=True)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

realtor_parser = RealtorParser()
for realtor_id in list(realtor_parser.get_realtors(100)):
    new_realtor = Realtor(id=realtor_id)
    session.add(new_realtor)
    session.commit()

session.close()
