import requests
from re import findall


class RealtorParser:
    """Класс для парсинга id риелторов с сайта циан"""

    @staticmethod
    def get_realtors(amount: int, regionId: int = 1):
        realtors_found = 0
        page_idx = 1
        while realtors_found < amount:
            r = requests.get(
                f"https://api.cian.ru/agent-catalog-search/v1/get-realtors/?regionId={regionId}&page={page_idx}&limit=10"
            )
            new_realtors = list(
                map(int, findall(r'(?<=cianUserId":)\d+', r.content.decode("utf-8")))
            )

            realtors_found += len(new_realtors)
            page_idx += 1
            for new_realtor in new_realtors:
                yield new_realtor


# https://www.cian.ru/agents
