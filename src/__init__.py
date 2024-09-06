from .db import Base, engine


def init_db():
    Base.metadata.create_all(engine)
