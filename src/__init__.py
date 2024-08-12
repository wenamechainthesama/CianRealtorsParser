from .db import Base, engine
# from .parser.realtors_id_parser import RealtorsIdParser
# from .db.interface import SQLInterface
# from .db.models import RealtorData, RealtorId


def init_db():
    Base.metadata.create_all(engine)


# __all__ = ["RealtorsIdParser", "SQLInterface", "RealtorId", "RealtorData"]
