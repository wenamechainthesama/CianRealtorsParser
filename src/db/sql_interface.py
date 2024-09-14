from loguru import logger

from .models import RealtorId, RealtorData, AdspowerInstance
from sqlalchemy.orm import Session


class SQLInterface:

    @staticmethod
    def write_realtors_ids(session: Session, realtors_ids: list):
        num_realtors_ids = len(realtors_ids)
        adspower_instance = AdspowerInstance.first
        for idx, realtor_id in enumerate(realtors_ids):
            if idx >= num_realtors_ids / 2:
                adspower_instance = AdspowerInstance.second
            id_already_in_db = session.query(
                session.query(RealtorId).filter_by(id=realtor_id).exists()
            ).scalar()
            if not id_already_in_db:
                new_realtor = RealtorId(
                    id=realtor_id, adspower_instance=adspower_instance
                )
                session.add(new_realtor)
            else:
                logger.warning(f"Этот id ({realtor_id}) уже есть в бд")

        session.commit()

        ids_count = session.query(RealtorId).count()
        logger.success(
            f"Ещё {len(realtors_ids)} ids риелторов добавлены в базу данных. Всего ids в бд: {ids_count}"
        )

    @staticmethod
    def get_realtors_ids(
        session: Session, adspower_instance: AdspowerInstance, batch_size=10
    ):
        result = [
            i[0]
            for i in session.query(RealtorId.id)
            .filter(
                RealtorId.already_used == 0,
                RealtorId.adspower_instance == adspower_instance,
                RealtorId.is_errored != True,
            )
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

    @staticmethod
    def mark_error_ids(session: Session, error_ids: list[int]):
        for id in error_ids:
            session.query(RealtorId).filter(RealtorId.id == id).update(
                {"is_errored": True}
            )

        session.commit()
