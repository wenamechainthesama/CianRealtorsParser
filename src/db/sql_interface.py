from .models import RealtorId
from sqlalchemy.orm import Session


class SQLInterface:

    @staticmethod
    def write_realtors_id(session: Session, realtors_ids: list):
        for realtor_id in realtors_ids:
            new_realtor = RealtorId(id=realtor_id)
            session.add(new_realtor)

        session.commit()

    @staticmethod
    def write_realtors_data(session: Session):
        pass
