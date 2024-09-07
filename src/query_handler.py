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
        # Создание объекта класса по парсингу id риелторов
        realtors_id_parser = RealtorsIdParser(
            proxies=QueryHandler.proxies,
            rotation_interval=QueryHandler.rotation_interval,
        )

        # Получение и запись в базу данных id риелторов частями
        for _ in range(5):
            # Получение
            realtors_ids = list(
                realtors_id_parser.get_realtors_ids(batch_size=QueryHandler.batch_size)
            )

            # Запись в бд
            SQLInterface.write_realtors_ids(session=session, realtors_ids=realtors_ids)

            # TODO: тоже добавить обработчик ошибок, так как если у тебя ошибка то код свалится

    @staticmethod
    def process_realtors_data():
        # TODO: добавить запрос к базе для получения ids
        # realtors_ids = [12284, 17657, 18867, 21934, 23097]
        realtors_ids = list(SQLInterface.get_realtors_ids(session=session))
        print(realtors_ids, len(realtors_ids))

        realtors_data_parser = RealtorsDataParser(
            realtor_ids=realtors_ids,
            proxies=QueryHandler.proxies,
            rotation_interval=QueryHandler.rotation_interval,
        )

        realtors_data_batch = realtors_data_parser.get_realtors_data()

        # print(realtors_data_batch)

        # TODO: добавить в базу полученные данные о риелторах
        # ...
