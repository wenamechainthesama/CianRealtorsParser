import time
import multiprocessing

from loguru import logger

from src.db.models import AdspowerInstance
from src.query_handler import QueryHandler
from config import ADSPOWER_ID1, ADSPOWER_ID2, ADSPOWER_NAME1, ADSPOWER_NAME2

logger.add("realtors_parser.log", format="{time} {level} {message}", level="INFO")


def fetch_ids():
    query_handler = QueryHandler()
    query_handler.process_realtors_id()


def fetch_realtor_data():
    query_handler = QueryHandler()
    task1 = multiprocessing.Process(
        target=query_handler.process_realtors_data,
        args=[ADSPOWER_ID1, ADSPOWER_NAME1, AdspowerInstance.first],
    )
    task1.start()
    task2 = multiprocessing.Process(
        target=query_handler.process_realtors_data,
        args=[ADSPOWER_ID2, ADSPOWER_NAME2, AdspowerInstance.second],
    )
    task2.start()
    task1.join()
    task2.join()


def main():
    fetch_ids()
    fetch_realtor_data()


if __name__ == "__main__":
    start = time.time()
    main()
    res = time.time() - start
    print(f"Время выполнения в секундах: {res}")
