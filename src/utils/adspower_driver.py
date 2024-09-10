import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from config import ADSPOWER_ID, ADSPOWER_NAME


class AdspowerDriver:
    """Класс для инициализации Adspower"""

    adspower_id = ADSPOWER_ID
    name = ADSPOWER_NAME

    @classmethod
    def get_browser(cls):
        open_url = (
            "http://local.adspower.com:50325/api/v1/browser/start?user_id="
            + cls.adspower_id
        )
        resp = requests.get(open_url).json()

        if resp["code"] != 0:
            print(resp["msg"])
            print("please check ads_id")
            exit()

        browser = resp["data"]["webdriver"]
        service = Service(executable_path=browser)
        chrome_options = Options()

        chrome_options.add_experimental_option(
            "debuggerAddress", resp["data"]["ws"]["selenium"]
        )

        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    @classmethod
    def delete_cache_adspower(cls):
        url = (
            "http://localhost:50325/api/v1/user/delete-cache?user_id=" + cls.adspower_id
        )
        requests.request("POST", url)

    @classmethod
    def change_proxy(cls, proxy_type, host, port, user, password):
        ua = UserAgent()
        user_agent = ua.random
        url = "http://local.adspower.net:50325/api/v1/user/update"
        proxy = {
            "proxy_soft": "other",
            "proxy_type": f"{proxy_type}",
            "proxy_host": f"{host}",
            "proxy_port": f"{port}",
            "proxy_user": f"{user}",
            "proxy_password": f"{password}",
        }
        payload = {
            "user_id": f"{cls.adspower_id}",
            "name": f"{cls.name}",
            "domain_name": "https://yandex.com",
            "repeat_config": ["0"],
            "open_urls": [
                "https://whoer.net/ru",
            ],
            "country": "ru",
            "remark": "remark",
            "fingerprint_config": {
                "automatic_timezone": "1",
                "language": ["en-US", "en"],
                "flash": "block",
                "fonts": ["all"],
                "webrtc": "proxy",
                "ua": user_agent,
            },
            "user_proxy_config": proxy,
        }

        headers = {"Content-Type": "application/json"}
        time.sleep(5)
        requests.post(url, headers=headers, json=payload)
        print(f"Статус изменения прокси -> {requests.status_code}")
