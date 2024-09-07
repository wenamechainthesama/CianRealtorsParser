from re import findall
import  random
import traceback
from typing import Iterator

import requests
from fake_useragent import UserAgent
from loguru import logger




class RealtorsIdParser:
    """Класс для парсинга id риелторов с сайта циан"""

    def __init__(self, proxies: list[dict[str, str]] | None, rotation_interval: int = 5):
        self.ua = UserAgent()
        self.proxies = proxies
        self.rotation_interval = rotation_interval
        self.request_count = 0
        self.current_proxy = self.get_random_proxy()

    def get_realtors_id(self,
                        amount: int,
                        regionId: int = 1) -> Iterator[int] | None:

        realtors_found = 0
        page_idx = 1

        # TODO: добавить обработчик ошибок на requests
        while realtors_found < amount:

            self.rotate_proxy()
            self.request_count += 1

            # TODO: добавить логирование
            headers = {
                "User-Agent": self.ua.random  # Fake user agent
            }

            try:
                r = requests.get(
                    f"https://api.cian.ru/agent-catalog-search/v1/get-realtors/?regionId={regionId}&page={page_idx}&limit=10"
                ,
                proxies={"http": self.current_proxy, "https": self.current_proxy} if self.current_proxy else None,
                headers=headers,
                timeout=10) # TODO: проверить максимальный лимит по запросам ids

                if r.status_code in range(200, 400):
                    # ALL GOOD
                    new_realtors = list(
                        map(int, findall(r'(?<=cianUserId":)\d+', r.content.decode("utf-8")))
                    )

                    realtors_found += len(new_realtors)
                    page_idx += 1
                    for new_realtor in new_realtors:
                        yield new_realtor
                else:
                    # TODO: добавить ротацию прокси, добавить слип долгий
                    pass
            except Exception:
                logger.error(f"Ошибка при сборе ids - {traceback.format_exc()}")
                return


    def get_random_proxy(self) -> dict[str, str]:
        """Возвращает случайный прокси из списка"""
        return random.choice(self.proxies) if self.proxies else None

    def rotate_proxy(self):
        """Меняет прокси после каждых n запросов"""
        if self.request_count % self.rotation_interval == 0:
            self.current_proxy = self.get_random_proxy()
            """
            self.current_proxy
            {
                "PROXY_HOST": ...,
                "PROXY_PORT": ...,
                "PROXY_PSW": ...,
                "PROXY_LOGIN": ...,
                
            }   
            """
            # TODO: получаем словарь с данными прокси и его нужно преобразовать в строку, чтобы отдать в requests
            logger.info(f"Proxy rotated: {self.current_proxy}")

