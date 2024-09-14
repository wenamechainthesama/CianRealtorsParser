import time
import random
import traceback

from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from ..db import session
from ..db.sql_interface import SQLInterface
from src.utils.adspower_driver import AdspowerDriver


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
                realtor_contacts = WebDriverWait(adspower_browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[@data-name='RealtorContacts']")
                    )
                )
                show_phone_button = WebDriverWait(realtor_contacts, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "_3ea6fa5da8--color_primary_100--AuVro")
                    )
                )
                ActionChains(adspower_browser).click(show_phone_button).perform()
                time.sleep(random.randint(1, 2))
                phone_number = (
                    WebDriverWait(realtor_contacts, 10)
                    .until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//*[@data-name='RealtorContactsLink']")
                        )
                    )
                    .text
                )
                social_items = WebDriverWait(realtor_contacts, 10).until(
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
            except Exception:
                logger.error(
                    f"При сборе данных риелтора (id={id}):\n{traceback.format_exc()}"
                )
                error_ids.append(id)

        logger.success(f"Получены данные ещё о {data_parsed_counter} риелторах")
        self.rotate_proxy(adspower_id=adspower_id, adspower_name=adspower_name)
        SQLInterface.mark_error_ids(session=session, error_ids=error_ids)

    def get_random_proxy(self) -> dict[str, str]:
        """Возвращает случайный прокси из списка"""
        return random.choice(self.proxies) if self.proxies else None

    def rotate_proxy(self, adspower_id: str, adspower_name: str):
        """Меняет прокси после каждых n запросов"""
        self.current_proxy = self.get_random_proxy()

        if self.current_proxy:
            proxy_type = "HTTP"

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
