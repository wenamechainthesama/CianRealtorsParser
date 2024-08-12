from .models import RealtorId

class SQLInterface:
    @staticmethod
    def write_realtors_id(session, realtors_ids: list):
        for realtor_id in realtors_ids:
            new_realtor = RealtorId(id=realtor_id)
            session.add(new_realtor)

        session.commit()

    def write_realtors_data(session):
        pass
