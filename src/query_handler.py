from loguru import logger

from .db.sql_interface import SQLInterface
from .parser.realtors_id_parser import RealtorsIdParser
from .parser.realtors_data_parser import RealtorsDataParser
from .db import session
from config import proxy_list


class QueryHandler:
    """
    Основной класс для запуска парсеров
    и передавания данных в бд
    """

    proxies = None  # proxy_list
    rotation_interval = 10
    batch_size = 10

    @staticmethod
    def process_realtors_id():
        # Создание объекта класса по парсингу ids риелторов
        realtors_id_parser = RealtorsIdParser(
            proxies=QueryHandler.proxies,
            batch_size=QueryHandler.batch_size,
        )

        # Получение и запись в базу данных ids риелторов частями
        # realtors_ids = True
        # while realtors_ids:
        for _ in range(3):
            # Получение
            realtors_ids = list(realtors_id_parser.parse_realtors_ids())
            logger.success(f"Получены новые {QueryHandler.batch_size} ids")

            # Запись в бд
            SQLInterface.write_realtors_ids(session=session, realtors_ids=realtors_ids)
            logger.success(
                f"Ещё {QueryHandler.batch_size} ids риелторов добавлены в базу данных"
            )

    @staticmethod
    def process_realtors_data():
        realtors_data_parser = RealtorsDataParser(
            proxies=QueryHandler.proxies,
            batch_size=QueryHandler.batch_size,
        )

        while True:
            realtors_ids_batch = list(SQLInterface.get_realtors_ids(session=session))
            if not realtors_ids_batch:
                break
            realtors_data_batch = list(
                realtors_data_parser.get_realtors_data(
                    realtors_ids_batch=realtors_ids_batch
                )
            )
            logger.success(f"Получены данные ещё о {QueryHandler.batch_size} риелторах")
            print(len(realtors_data_batch))
            SQLInterface.write_realtors_data(
                session=session, realtors_data=realtors_data_batch
            )
            logger.success(
                f"Сохранены данные ещё о {QueryHandler.batch_size} риелторах"
            )
        logger.success("Все риелторы добавлены в базу данных")
