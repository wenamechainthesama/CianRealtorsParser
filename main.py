import asyncio
from src.query_handler import QueryHandler


async def main():
    query_handler = QueryHandler()
    await query_handler.process_realtors_id()


if __name__ == "__main__":
    asyncio.run(main())
