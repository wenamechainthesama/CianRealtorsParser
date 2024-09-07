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

    @staticmethod
    def process_realtors_id():
        # TODO: как нам обрабатывать ids, которые уже собрали, чтобы в случае ошибки не начинать парсинг заново?
        amount = 100
        # TODO: убрать Крым и Севастополь по ids
        regionIds = [i for i in range(1, 88) if i != 86 or i != 56]


        for regionId in regionIds:
            logger.info(f"Сбора ids по региону {regionId}")

            realtors_id_parser = RealtorsIdParser(proxies=QueryHandler.proxies,
                                                  rotation_interval=QueryHandler.rotation_interval)

            # TODO: тоже добавить обработчик ошибок, так как если у тебя ошибка то код свалится

            realtors_ids = realtors_id_parser.get_realtors_id(amount=amount,
                                                                   regionId=regionId)

            if realtors_ids:
                realtors_ids = list(realtors_ids)
                SQLInterface.write_realtors_id(session, realtors_ids)
            else:
                # TODO добавить логирование
                pass

    @staticmethod
    def process_realtors_data():

        # TODO: добавить запрос к базе для получения ids
        realtor_ids = [12284, 17657, 18867, 21934, 23097]

        realtor_data_parser = RealtorsDataParser(realtor_ids=realtor_ids,
                                                 proxies=QueryHandler.proxies,
                                                 rotation_interval=QueryHandler.rotation_interval)

        realtor_data_parser.get_realtors_data()


