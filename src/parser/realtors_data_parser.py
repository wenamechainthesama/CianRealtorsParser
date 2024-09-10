import random

import requests
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import sys

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

            name = adspower_driver.find_element(
                By.XPATH,
                '//*[@id="realtor-reviews-frontend"]/div/div[2]/main/section[1]/div[1]/div[2]/div/span/span/span[1]',
            )
            print(name.text)
            region = adspower_driver.find_element(
                By.XPATH,
                '//*[@id="realtor-reviews-frontend"]/div/div[2]/main/section[1]/div[3]/div[3]/span/span',
            )
            print(region.text)
            show_phone_btn = adspower_driver.find_element(
                By.XPATH, '//*[@id="realtor-contacts"]/div/div[1]/div/span[2]'
            )
            show_phone_btn.click()
            time.sleep(3)
            phone_number = adspower_driver.find_element(
                By.XPATH, '//*[@id="realtor-contacts"]/div/div[1]/div/a/span'
            )
            print(phone_number.text)

            self.request_count += 1

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


def test_get_cian_realtor():
    ads_id = "kmg4vf7"  # "jg1ypsy"
    open_url = "http://local.adspower.com:50325/api/v1/browser/start?user_id=" + ads_id
    close_url = "http://local.adspower.com:50325/api/v1/browser/stop?user_id=" + ads_id

    resp = requests.get(open_url).json()

    if resp["code"] != 0:
        print(resp["msg"])
        print("please check ads_id")
        sys.exit()

    chrome_driver = resp["data"]["webdriver"]
    service = Service(executable_path=chrome_driver)
    chrome_options = Options()

    chrome_options.add_experimental_option(
        "debuggerAddress", resp["data"]["ws"]["selenium"]
    )
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(
        "https://www.cian.ru/realtors/?dealType=rent&offerType%5B0%5D=flat&regionId=1&page=1"
    )
    time.sleep(3)

    realtors_ids = [12284, 17657, 18867, 21934, 23097]
    realtors_link = "https://www.cian.ru/agents/"

    for id in realtors_ids:
        driver.get(realtors_link + str(id))
        name = driver.find_element(
            By.XPATH,
            '//*[@id="realtor-reviews-frontend"]/div/div[2]/main/section[1]/div[1]/div[2]/div/span/span/span[1]',
        )
        print(name.text)
        region = driver.find_element(
            By.XPATH,
            '//*[@id="realtor-reviews-frontend"]/div/div[2]/main/section[1]/div[3]/div[3]/span/span',
        )
        print(region.text)
        show_phone_btn = driver.find_element(
            By.XPATH, '//*[@id="realtor-contacts"]/div/div[1]/div/span[2]'
        )
        show_phone_btn.click()
        time.sleep(3)
        phone_number = driver.find_element(
            By.XPATH, '//*[@id="realtor-contacts"]/div/div[1]/div/a/span'
        )
        print(phone_number.text)
        # email = driver.find_element(By.XPATH, '//*[@id="realtor-contacts"]/div/div[2]/div/a/span')
        # print(email.text)

    driver.quit()
    requests.get(close_url)
