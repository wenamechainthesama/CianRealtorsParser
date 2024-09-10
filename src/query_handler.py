from loguru import logger

from .db.sql_interface import SQLInterface
from .parser.realtors_id_parser import RealtorsIdParser
from .parser.realtors_data_parser import RealtorsDataParser
from .db import session


class QueryHandler:
    """
    Основной класс для запуска парсеров
    и передавания данных в бд
    """

    proxies = None  # список прокси
    rotation_interval = 10
    batch_size = 10

    @staticmethod
    def process_realtors_id():
        # Создание объекта класса по парсингу ids риелторов
        realtors_id_parser = RealtorsIdParser(
            proxies=QueryHandler.proxies,
            rotation_interval=QueryHandler.rotation_interval,
        )

        # Получение и запись в базу данных ids риелторов частями
        # realtors_ids = True
        # while realtors_ids:
        for _ in range(3):
            # Получение
            realtors_ids = list(
                realtors_id_parser.parse_realtors_ids(
                    batch_size=QueryHandler.batch_size
                )
            )
            logger.success(f"Получены новые {QueryHandler.batch_size} ids")

            # Запись в бд
            SQLInterface.write_realtors_ids(session=session, realtors_ids=realtors_ids)
            logger.success(
                f"Ещё {QueryHandler.batch_size} ids риелторов добавлены в базу данных"
            )
            # TODO: тоже добавить обработчик ошибок, так как если у тебя ошибка то код свалится

    @staticmethod
    def process_realtors_data():
        realtors_ids = list(SQLInterface.get_realtors_ids(session=session))

        realtors_data_parser = RealtorsDataParser(
            realtor_ids=realtors_ids,
            proxies=QueryHandler.proxies,
            rotation_interval=QueryHandler.rotation_interval,
        )

        realtors_data_batch = True
        while realtors_data_batch:
            realtors_data_batch = list(realtors_data_parser.get_realtors_data())
            logger.success(f"Получены данные ещё о {QueryHandler.batch_size} риелторах")
            print(len(realtors_data_batch))
            SQLInterface.write_realtors_data(
                session=session, realtors_data=realtors_data_batch
            )
            logger.success(
                f"Сохранены данные ещё о {QueryHandler.batch_size} риелторах"
            )
        logger.success("Все риелторы добавлены в базу данных")
