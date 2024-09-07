from loguru import  logger

from src.query_handler import QueryHandler

# Initialize loguru logger
logger.add("realtors_parser.log", format="{time} {level} {message}", level="INFO")

def fetch_ids():
    query_handler = QueryHandler()
    query_handler.process_realtors_id()

def fetch_realtor_data():
    query_handler = QueryHandler()
    query_handler.process_realtors_data()

def main():
    # fetch_ids()
    fetch_realtor_data()


if __name__ == "__main__":
    main()
