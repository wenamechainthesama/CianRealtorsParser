import os
from dotenv import load_dotenv
from src.parser.proxy_status import ProxyStatus

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
ADSPOWER_ID1 = os.environ.get("ADSPOWER_ID1")
ADSPOWER_ID2 = os.environ.get("ADSPOWER_ID2")
ADSPOWER_NAME1 = os.environ.get("ADSPOWER_NAME1")
ADSPOWER_NAME2 = os.environ.get("ADSPOWER_NAME2")

PROXIES = [
    [
        {
            "PROXY_HOST": "45.8.156.179",
            "PROXY_PORT": "6913",
            "PROXY_PSW": "yuljvh",
            "PROXY_LOGIN": "user163014",
        },
        ProxyStatus.ready,
    ],
    [
        {
            "PROXY_HOST": "176.56.36.117",
            "PROXY_PORT": "6913",
            "PROXY_PSW": "yuljvh",
            "PROXY_LOGIN": "user163014",
        },
        ProxyStatus.ready,
    ],
    [
        {
            "PROXY_HOST": "176.56.35.182",
            "PROXY_PORT": "6913",
            "PROXY_PSW": "yuljvh",
            "PROXY_LOGIN": "user163014",
        },
        ProxyStatus.ready,
    ],
    [
        {
            "PROXY_HOST": "212.115.50.125",
            "PROXY_PORT": "6913",
            "PROXY_PSW": "yuljvh",
            "PROXY_LOGIN": "user163014",
        },
        ProxyStatus.ready,
    ],
    [
        {
            "PROXY_HOST": "45.145.3.103",
            "PROXY_PORT": "6913",
            "PROXY_PSW": "yuljvh",
            "PROXY_LOGIN": "user163014",
        },
        ProxyStatus.ready,
    ],
    [
        {
            "PROXY_HOST": "194.32.124.131",
            "PROXY_PORT": "6913",
            "PROXY_PSW": "yuljvh",
            "PROXY_LOGIN": "user163014",
        },
        ProxyStatus.ready,
    ],
    [
        {
            "PROXY_HOST": "194.32.124.235",
            "PROXY_PORT": "6913",
            "PROXY_PSW": "yuljvh",
            "PROXY_LOGIN": "user163014",
        },
        ProxyStatus.ready,
    ],
    [
        {
            "PROXY_HOST": "176.56.35.101",
            "PROXY_PORT": "6913",
            "PROXY_PSW": "yuljvh",
            "PROXY_LOGIN": "user163014",
        },
        ProxyStatus.ready,
    ],
    [
        {
            "PROXY_HOST": "194.32.124.207",
            "PROXY_PORT": "6913",
            "PROXY_PSW": "yuljvh",
            "PROXY_LOGIN": "user163014",
        },
        ProxyStatus.ready,
    ],
    [
        {
            "PROXY_HOST": "194.34.250.145",
            "PROXY_PORT": "6913",
            "PROXY_PSW": "yuljvh",
            "PROXY_LOGIN": "user163014",
        },
        ProxyStatus.ready,
    ],
]
