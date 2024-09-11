from loguru import logger

from .models import RealtorId, RealtorData
from sqlalchemy.orm import Session


class SQLInterface:

    @staticmethod
    def write_realtors_ids(session: Session, realtors_ids: list):
        for realtor_id in realtors_ids:
            new_realtor = RealtorId(id=realtor_id)
            session.add(new_realtor)

        session.commit()

        ids_count = session.query(RealtorId).count()
        logger.success(
            f"Ещё {len(realtors_ids)} ids риелторов добавлены в базу данных. Всего ids в бд: {ids_count}"
        )

    @staticmethod
    def get_realtors_ids(session: Session, batch_size=10):
        result = [
            i[0]
            for i in session.query(RealtorId.id)
            .filter(RealtorId.already_used == 0)
            .limit(batch_size)
            .all()
        ]
        logger.info(f"Из бд взяты {len(result)} риелторов")
        return result

    @staticmethod
    def write_realtors_data(session: Session, realtors_data: list[dict[str, str]]):
        for data in realtors_data:
            new_data = RealtorData(
                name=data["name"],
                email=data["email"],
                phone_number=data["phone_number"],
                realtor_id=int(data["id"]),
            )
            session.add(new_data)
            session.query(RealtorId).filter(RealtorId.id == int(data["id"])).update(
                {"already_used": True}
            )

        session.commit()

        data_count = session.query(RealtorId).count()
        logger.success(
            f"Сохранены данные ещё о {len(realtors_data)} риелторах. Всего данных в бд: {data_count}"
        )
