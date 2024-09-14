import re
import time
import random
import traceback

from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from ..db import session
from ..db.sql_interface import SQLInterface
from src.utils.adspower_driver import AdspowerDriver

MAX_ATTEMPTS = 4

class RealtorsDataParser:
    """Класс для парсинга основных данных (имени, города, телефона, почты) риелторов с сайта циан"""

    def __init__(self, proxies: list[str], batch_size: int = 10):

        # self.is_first_instance = False
        self.proxies = proxies
        self.batch_size = batch_size
        self.adspower_driver: AdspowerDriver = AdspowerDriver()
        self.base_endpoint = "https://www.cian.ru/agents/"
        self.current_proxy = self.get_random_proxy()
        self.delay = None

    def get_realtors_data(
        self, realtors_ids_batch: list[int], adspower_id: str, adspower_name: str
    ):
        adspower_browser = self.adspower_driver.get_browser(adspower_id=adspower_id)
        data_parsed_counter = 0
        error_ids = []
        for id in realtors_ids_batch:
            try:
                realtor_link = self.base_endpoint + str(id)
                adspower_browser.get(realtor_link)
                time.sleep(random.randint(1, 2))

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
                realtor_contacts = WebDriverWait(adspower_browser, 3).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[@data-name='RealtorContacts']")
                    )
                )

                adspower_browser.execute_script("window.scrollBy(0, 300);")

                time.sleep(random.randint(1, 2))

                for i in range(MAX_ATTEMPTS):
                    if i > 0:
                        time.sleep(random.randint(1, 2))
                    logger.info(f"Ищу телефон. Попытка № {i + 1}")
                    phone_number = self.find_phone(realtor_contacts=realtor_contacts,
                                    adspower_browser=adspower_browser)
                    if phone_number:
                        logger.success(f"Телефон найден - {phone_number}")
                        break

                if phone_number is None:
                    logger.warning(f"Телефон не найден id - {id}")
                    raise Exception

                social_items = WebDriverWait(realtor_contacts, 3).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//*[@data-name='SocialItem']")
                    )
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

                data_parsed_counter += 1
                self.adspower_driver.delete_cache_adspower(adspower_id=adspower_id)

                time.sleep(self.delay if self.delay else random.randint(3, 4))

                logger.info(f"Данные по id - {id} успешно собраны")
            except Exception:
                logger.error(
                    f"При сборе данных риелтора (id={id}):\n{traceback.format_exc()}"
                )
                error_ids.append(id)

        logger.success(f"Получены данные ещё о {data_parsed_counter} риелторах")
        self.rotate_proxy(adspower_id=adspower_id, adspower_name=adspower_name)
        SQLInterface.mark_error_ids(session=session, error_ids=error_ids)

    def find_phone(self, realtor_contacts: WebElement,
                   adspower_browser: webdriver.Chrome) -> str | None:

        show_phone_button = WebDriverWait(realtor_contacts, 2).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "_3ea6fa5da8--color_primary_100--AuVro")
            )
        )

        for _ in range(2):
            time.sleep(random.randint(1, 2))
            try:
                ActionChains(adspower_browser).click(show_phone_button).perform()
            except Exception:
                pass

        adspower_browser.execute_script("window.scrollBy(0, 100);")

        try:
            phone_number = (
                WebDriverWait(realtor_contacts, 1)
                .until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[@data-name='RealtorContactsLink']")
                    )
                )
                .text
            )
            return phone_number
        except Exception:
            # Регулярное выражение для поиска номера телефона
            phone_regex = r"\+7 \d{3} \d{3}-\d{2}-\d{2}"

            # Извлечение всей HTML-страницы
            all_html = adspower_browser.page_source

            # Поиск телефона в HTML с помощью регулярного выражения
            phone_match = re.search(phone_regex, all_html)

            if phone_match:
                phone_number = phone_match.group(0)  # Если телефон найден, извлекаем его
                return phone_number
            else:
                return None



    def get_random_proxy(self) -> dict[str, str]:
        """Возвращает случайный прокси из списка"""
        return random.choice(self.proxies) if self.proxies else None

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
