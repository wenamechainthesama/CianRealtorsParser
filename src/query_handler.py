from .db.interface import SQLInterface
from .parser.realtors_id_parser import RealtorsIdParser
from .db import session


class QueryHandler:
    """
    Основной класс для запуска парсеров
    и передавания данных в бд
    """

    @staticmethod
    def process_realtors_id():
        realtors_id_parser = RealtorsIdParser()
        realtors_ids = list(realtors_id_parser.get_realtors_id(100))
        SQLInterface.write_realtors_data(session, realtors_ids)
