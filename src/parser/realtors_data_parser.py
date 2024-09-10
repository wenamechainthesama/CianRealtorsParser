import sys
import time
import random

import requests
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from src.utils.adspower_driver import AdspowerDriver


class RealtorsDataParser:
    """Класс для парсинга основных данных (имени, города, телефона, почты) риелторов с сайта циан"""

    def __init__(
        self, realtor_ids: list[int], proxies: list[str], rotation_interval: int
    ):

        self.realtor_ids = realtor_ids
        self.proxies = proxies
        self.request_count = 0
        self.rotation_interval = rotation_interval
        self.adspower_driver: AdspowerDriver = AdspowerDriver()
        self.base_endpoint = "https://www.cian.ru/agents/"
        self.current_proxy = self.get_random_proxy()

    def get_realtors_data(self):
        adspower_driver = self.adspower_driver.get_browser()
        for id in self.realtor_ids:
            # TODO: добавить логирование
            self.rotate_proxy()

            realtor_link = self.base_endpoint + str(id)
            adspower_driver.get(realtor_link)

            # Парсинг данных
            # Имя
            name = (
                WebDriverWait(adspower_driver, 5)
                .until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[@data-name='RealtorName']")
                    )
                )
                .text
            )

            # Регион работы
            description_rows = WebDriverWait(adspower_driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//*[@data-name='DescriptionRow']")
                )
            )
            for row in description_rows:
                title = row.find_element(
                    By.CLASS_NAME, "_3ea6fa5da8--about-title--OCzbj"
                )
                if title.text == "Регион работы":
                    region = row.find_element(
                        By.CLASS_NAME, "_3ea6fa5da8--about-text--xx5UG"
                    ).text

            # Номер телефона и почта
            realtor_contacts = WebDriverWait(adspower_driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@data-name='RealtorContacts']")
                )
            )
            show_phone_button = realtor_contacts.find_element(
                By.CLASS_NAME, "_3ea6fa5da8--color_primary_100--AuVro"
            )
            show_phone_button.click()
            phone_number = realtor_contacts.find_element(
                By.XPATH, "//*[@data-name='RealtorContactsLink']"
            ).text

            social_items = realtor_contacts.find_elements(
                By.XPATH, "//*[@data-name='SocialItem']"
            )

            for item in social_items:
                if item.text.__contains__("@"):
                    email = item.text

            yield {
                "id": str(id),
                "name": name,
                "region": region,
                "phone_number": phone_number,
                "email": email,
            }

        return False

    def get_random_proxy(self) -> dict[str, str]:
        """Возвращает случайный прокси из списка"""
        return random.choice(self.proxies) if self.proxies else None

    def rotate_proxy(self):
        """Меняет прокси после каждых n запросов"""
        if self.request_count % self.rotation_interval == 0:
            self.current_proxy = self.get_random_proxy()

            if self.current_proxy:
                # TODO: посмотреть в документации adspower тип прокси, но там - http или socks5
                proxy_type = ...

                self.adspower_driver.change_proxy(
                    proxy_type=proxy_type,
                    host=self.current_proxy["PROXY_HOST"],
                    port=self.current_proxy["PROXY_PORT"],
                    user=self.current_proxy["PROXY_LOGIN"],
                    password=self.current_proxy["PROXY_PSW"],
                )
                logger.info(
                    f"Изменено прокси при парсинге данных риелторов. Новое прокси: {self.current_proxy}"
                )
                # time.sleep(5)


# headers = {
#     "User-Agent": "My User Agent 1.0",
#     "From": "youremail@domain.example",  # This is another valid field
# }
