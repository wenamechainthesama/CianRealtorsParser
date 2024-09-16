import time
import random
import traceback

from pywinauto import Application
import pygetwindow as gw
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from .proxy_status import ProxyStatus
from ..db import session
from ..db.sql_interface import SQLInterface
from src.utils.adspower_driver import AdspowerDriver


class RealtorsDataParser:
    """Класс для парсинга основных данных (имени, города, телефона, почты) риелторов с сайта циан"""

    realtors_parsed: int = 0
    current_proxies: dict[str, ProxyStatus] = {}

    def __init__(
        self,
        proxies: list[list[dict[str, str], ProxyStatus]],
        proxy_rotation_delay_per_adspower_instance: int,
    ):
        RealtorsDataParser.current_proxies = proxies
        self.proxy_rotation_delay_per_adspower_instance = (
            proxy_rotation_delay_per_adspower_instance
        )
        self.adspower_driver: AdspowerDriver = AdspowerDriver()
        self.base_endpoint = "https://www.cian.ru/agents/"
        self.current_proxy = self.get_random_proxy()
        self.phone_max_attempts = 4
        self.request_counter = 0
        self.delay = None

    def get_realtors_data(
        self, realtors_ids_batch: list[int], adspower_id: str, adspower_name: str
    ):
        adspower_browser = self.adspower_driver.get_browser(adspower_id=adspower_id)
        data_parsed_counter = 0
        error_ids = []
        broken_ids = []
        for id in realtors_ids_batch:
            try:
                realtor_link = self.base_endpoint + str(id)
                adspower_browser.get(realtor_link)
                self.request_counter += 1
                time.sleep(random.randint(1, 2))

                title = (
                    WebDriverWait(adspower_browser, 5)
                    .until(EC.presence_of_element_located((By.CLASS_NAME, "title")))
                    .text
                )
                if title == "Страница не найдена":
                    broken_ids.append(id)
                    continue

                # Парсинг данных
                # Имя
                name = (
                    WebDriverWait(adspower_browser, 5)
                    .until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//*[@data-name='RealtorName']")
                        )
                    )
                    .text
                )

                # if (
                #     self.request_counter
                #     - 1 % self.proxy_rotation_delay_per_adspower_instance
                #     == 0
                # ):
                #     # Фокусировка на окне
                #     window_list = gw.getWindowsWithTitle(
                #         f"{name} - риэлтор, контакты, объекты риэлтора"
                #     )
                #     if window_list:
                #         browser_window = window_list[0]
                #         browser_window.activate()
                #         app = Application().connect(handle=browser_window._hWnd)
                #         app_dialog = app.top_window()
                #         app_dialog.set_focus()
                #         app_dialog.always_on_top()

                # Регион работы
                description_rows = WebDriverWait(adspower_browser, 5).until(
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
                realtor_contacts = WebDriverWait(adspower_browser, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[@data-name='RealtorContacts']")
                    )
                )

                for i in range(self.phone_max_attempts):
                    time.sleep(1)
                    logger.info(f"Ищу телефон. Попытка № {i + 1}")
                    phone_number = self.find_phone(
                        realtor_contacts=realtor_contacts,
                        adspower_browser=adspower_browser,
                    )
                    if phone_number:
                        logger.info(f"Телефон найден - {phone_number}")
                        break

                if phone_number is None:
                    logger.warning(f"Телефон не найден (id={id})")
                    raise Exception

                email = None
                try:
                    social_items = WebDriverWait(realtor_contacts, 5).until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, "//*[@data-name='SocialItem']")
                        )
                    )
                    for item in social_items:
                        if item.text.__contains__("@"):
                            email = item.text
                except Exception:
                    pass

                yield {
                    "id": str(id),
                    "name": name,
                    "region": region,
                    "phone_number": phone_number,
                    "email": email,
                }

                data_parsed_counter += 1
                RealtorsDataParser.realtors_parsed += 1
                self.adspower_driver.delete_cache_adspower(adspower_id=adspower_id)

                # if (
                #     self.request_counter
                #     % self.proxy_rotation_delay_per_adspower_instance
                #     == 0
                # ):
                #     self.rotate_proxy(
                #         adspower_id=adspower_id, adspower_name=adspower_name
                #     )
                #     time.sleep(random.randint(2, 3))
                # adspower_browser = self.adspower_driver.get_browser(
                #     adspower_id=adspower_id
                # )

                time.sleep(self.delay if self.delay else random.randint(3, 4))

                logger.success(
                    f"Данные по id - {id} успешно собраны (adspower_instance={adspower_name[-1]}). Всего этим adspower instance собрано {RealtorsDataParser.realtors_parsed} ids из 31948"
                )
                with open("data_checkpoint.txt", "w", encoding="utf-8") as file:
                    file.write(
                        f"id = {id} realtors_parsed = {RealtorsDataParser.realtors_parsed}"
                    )
            except Exception:
                logger.error(
                    f"При сборе данных риелтора (id={id}):\n{traceback.format_exc()}"
                )
                # self.rotate_proxy(adspower_id=adspower_id, adspower_name=adspower_name)
                error_ids.append(id)

        logger.info(f"Получены данные ещё о {data_parsed_counter} риелторах")
        SQLInterface.mark_error_ids(session=session, error_ids=error_ids)
        SQLInterface.mark_broken_ids(session=session, broken_ids=broken_ids)

    def find_phone(
        self, realtor_contacts: WebElement, adspower_browser: webdriver.Chrome
    ) -> str:
        show_phone_button = WebDriverWait(realtor_contacts, 2).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "_3ea6fa5da8--color_primary_100--AuVro")
            )
        )
        ActionChains(adspower_browser).click(show_phone_button).perform()
        phone_number = WebDriverWait(realtor_contacts, 1).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@data-name='RealtorContactsLink']")
            )
        )
        return phone_number.text if phone_number else None

    def get_random_proxy(self) -> dict[str, str]:
        """Возвращает случайный прокси из списка"""
        if RealtorsDataParser.current_proxies is None:
            return None
        ready_proxies = [
            item
            for item in self.current_proxies
            if item[1] not in [ProxyStatus.busy, ProxyStatus.banned]
        ]
        chosen_list = random.choice(ready_proxies)
        chosen_proxy = chosen_list[0]
        RealtorsDataParser.current_proxies[
            RealtorsDataParser.current_proxies.index(chosen_list)
        ][1] = ProxyStatus.busy
        return chosen_proxy

    def rotate_proxy(self, adspower_id: str, adspower_name: str):
        """Меняет прокси после каждых n запросов"""
        self.current_proxy = self.get_random_proxy()

        if self.current_proxy:
            proxy_type = "http"

            self.adspower_driver.change_proxy(
                adspower_id=adspower_id,
                adspower_name=adspower_name,
                proxy_type=proxy_type,
                host=self.current_proxy["PROXY_HOST"],
                port=self.current_proxy["PROXY_PORT"],
                user=self.current_proxy["PROXY_LOGIN"],
                password=self.current_proxy["PROXY_PSW"],
            )
            logger.info(
                f"Изменено прокси при парсинге данных риелторов. Новое прокси: {self.current_proxy}"
            )
