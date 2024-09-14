from re import findall
import random
import traceback
import time
from typing import Iterator

import requests
from fake_useragent import UserAgent
from loguru import logger

from .proxy_status import ProxyStatus


class RealtorsIdParser:
    """Класс для парсинга id риелторов с сайта циан"""

    current_proxies_str: dict[str, ProxyStatus] = {}

    def __init__(
        self, proxies: list[list[dict[str, str], ProxyStatus]], batch_size: int = 10
    ):
        self.proxies = proxies
        self.current_proxy = None
        self.useragent = UserAgent()

        self.batch_size = batch_size
        self.forbidden_regions_idxs = [181462, 184723]
        self.regions_ids = None
        self.realtors_found_global = 0

        self.current_page_idx = int(
            input("Введите страницу, с которой начнется парсинг: ")
        )
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
        logger.debug(f"{self.regions_ids}")
        self.current_region_idx = int(
            input("Введите индекс региона, с которого начнется парсинг: ")
        )
        logger.info("Все регионы РФ, кроме Крыма и Севастополя, получены")

    def translate_proxies_into_strings(self):
        for item in self.proxies:
            proxy = item[0]
            status = item[1]
            current_proxy = f"http://{proxy['PROXY_LOGIN']}:{proxy['PROXY_PSW']}@{proxy['PROXY_HOST']}:{proxy['PROXY_PORT']}"
            self.current_proxies_str.setdefault(current_proxy, status)
        logger.info(
            f"Все прокси преобразованы в строки. Список прокси: {self.current_proxies_str}"
        )

    def parse_realtors_ids(self) -> Iterator[int]:
        realtors_found_local = 0
        while realtors_found_local < self.batch_size:
            try:
                proxy = self.get_random_proxy()
                request = requests.get(
                    f"https://api.cian.ru/agent-catalog-search/v1/get-realtors/?dealType=rent&offerType%5B0%5D=flat&regionId={self.regions_ids[self.current_region_idx]}&page={self.current_page_idx}",
                    proxies=({"http": proxy, "https": proxy}),
                    headers={
                        "user-agent": self.useragent.random,
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                )
                RealtorsIdParser.current_proxies_str[proxy] = ProxyStatus.ready
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
                        with open("ids_checkpoint.txt", "w", encoding="utf-8") as file:
                            file.write(
                                f"page_index = {self.current_page_idx} region_idx = {self.current_region_idx}"
                            )
                        logger.success(
                            f"Получены новые {self.batch_size} ids (proxy={proxy}). Получено всего ids: {self.realtors_found_global}"
                        )
                        time.sleep(self.delay if self.delay else random.randint(2, 3))
                else:
                    logger.error(
                        f"Не загружается страница циана. Код статуса: {request.status_code}"
                    )
                    RealtorsIdParser.current_proxies_str[proxy] = ProxyStatus.banned

            except Exception:
                logger.error(f"Ошибка при сборе ids:\n{traceback.format_exc()}")

    def get_random_proxy(self) -> dict[str, str]:
        """Возвращает случайный прокси из списка"""
        if self.proxies is None:
            return None
        ready_proxies = [
            proxy
            for proxy, status in self.current_proxies_str.items()
            if status not in [ProxyStatus.busy, ProxyStatus.banned]
        ]
        chosen_proxy = random.choice(ready_proxies)
        RealtorsIdParser.current_proxies_str[chosen_proxy] = ProxyStatus.busy
        return chosen_proxy
