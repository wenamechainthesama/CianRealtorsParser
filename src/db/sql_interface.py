from .models import RealtorId
from sqlalchemy.orm import Session


class SQLInterface:

    @staticmethod
    def write_realtors_ids(session: Session, realtors_ids: list):
        for realtor_id in realtors_ids:
            new_realtor = RealtorId(id=realtor_id)
            session.add(new_realtor)

        session.commit()

    @staticmethod
    def get_realtors_ids(session: Session, batch_size=10):
        result = [i[0] for i in session.query(RealtorId.id)]
        return result

    @staticmethod
    def write_realtors_data(session: Session):
        pass
