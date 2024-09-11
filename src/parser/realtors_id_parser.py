from re import findall
import random
import traceback
import time
from typing import Iterator

import requests
from fake_useragent import UserAgent
from loguru import logger


class RealtorsIdParser:
    """Класс для парсинга id риелторов с сайта циан"""

    def __init__(self, proxies: list[dict[str, str]] | None, batch_size: int = 10):
        self.ua = UserAgent()
        self.proxies = proxies
        self.current_proxy = None
        self.current_proxies_str: list[str] = None

        self.batch_size = batch_size
        self.request_count = 0
        self.forbidden_regions_idxs = [181462, 184723]
        self.regions_ids = None
        self.realtors_found_global = 0

        self.current_page_idx = 1
        self.current_region_idx = None

        self.delay = None

        self.get_regions_ids()
        if self.proxies:
            self.translate_proxies_into_strings()

    def get_regions_ids(self):
        request = requests.get(
            "https://api.cian.ru/geo-temp-layer/v1/get-federal-subjects-of-russia/"
        )
        self.regions_ids = [
            int(i)
            for i in findall(r'(?<="id":)\d+', request.content.decode("utf-8"))
            if int(i) not in self.forbidden_regions_idxs
        ]
        self.current_region_idx = 0

    def translate_proxies_into_strings(self):
        for proxy in self.proxies:
            current_proxy = f"{proxy["PORT"].lower()}://{proxy["USERNAME"]}:{proxy["PASSWORD"]}@{proxy["HOST"]}"
            print(current_proxy)
            self.current_proxies_str.append(current_proxy)

    def parse_realtors_ids(self) -> Iterator[int] | None:
        # TODO: добавить обработчик ошибок на requests
        # TODO: добавить логирование
        # TODO: как нам обрабатывать ids, которые уже собрали, чтобы в случае ошибки не начинать парсинг заново?
        # TODO: разобраться с прокси, добавить ротацию прокси, добавить слип долгий
        realtors_found_local = 0
        while realtors_found_local < self.batch_size:
            try:
                # TODO: добавить headers
                request = requests.get(
                    f"https://api.cian.ru/agent-catalog-search/v1/get-realtors/?dealType=rent&offerType%5B0%5D=flat&regionId={self.regions_ids[self.current_region_idx]}&page={self.current_page_idx}",
                    proxies=(
                        {"http": self.get_random_proxy(), "https": self.get_random_proxy()}
                    ),
                )
                if request.status_code in range(200, 400):
                    new_realtors = list(
                        map(
                            int,
                            findall(
                                r'(?<=cianUserId":)\d+', request.content.decode("utf-8")
                            ),
                        )
                    )
                    for new_realtor in new_realtors:
                        yield new_realtor

                    if new_realtors == []:
                        self.current_region_idx += 1
                        self.current_page_idx = 1

                        if self.current_region_idx >= len(self.regions_ids) - 1:
                            # Риелторы кончились
                            return False
                    else:
                        realtors_found_local += len(new_realtors)
                        self.realtors_found_global += len(new_realtors)
                        self.current_page_idx += 1
                        time.sleep(self.delay if self.delay else random.randint(2, 4))
                else:
                    logger.error(
                        f"Не загружается страница циана. Код статуса: {request.status_code}"
                    )

            except Exception:
                logger.error(f"Ошибка при сборе ids - {traceback.format_exc()}")

    def get_random_proxy(self) -> dict[str, str]:
        """Возвращает случайный прокси из списка"""
        return random.choice(self.current_proxies_str) if self.proxies else None
