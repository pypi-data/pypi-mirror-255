import random as r
from collections import OrderedDict
from datetime import datetime

from faker import Faker
from pydantic import BaseModel, Field

fake = Faker()


IP_LIST = [
    "75.154.230.69",
    "107.213.73.193",
    "8.180.44.74",
    "210.45.103.254",
    "181.122.97.1",
    "151.19.123.93",
    "192.174.20.196",
    "96.192.68.180",
    "43.143.218.20",
    "14.143.57.84",
    "108.109.27.190",
    "142.125.250.115",
    "17.182.173.27",
    "166.27.29.107",
    "178.147.45.115",
    "75.192.20.98",
    "132.92.18.244",
    "124.199.2.247",
    "47.98.109.177",
    "101.38.167.246",
    "4.118.98.143",
    "81.253.168.204",
    "45.242.251.37",
    "151.176.0.125",
    "171.103.3.147",
    "143.188.60.211",
    "190.117.141.137",
    "206.42.116.122",
    "154.66.193.152",
    "52.94.163.131",
    "25.58.69.196",
    "157.191.205.41",
    "74.115.140.157",
    "94.68.167.189",
    "63.225.201.204",
    "131.225.21.36",
    "209.226.110.111",
    "19.176.55.199",
    "198.155.186.52",
    "143.224.177.12",
    "175.237.120.144",
    "206.24.16.180",
    "181.236.121.75",
    "97.239.144.89",
    "72.99.39.145",
    "58.241.14.168",
    "42.17.140.223",
    "39.55.39.88",
    "173.49.111.146",
    "60.220.197.181",
    "159.201.154.151",
    "109.55.52.66",
    "178.2.209.107",
    "121.56.124.52",
    "103.170.136.111",
    "205.123.124.197",
    "147.100.122.234",
    "203.180.211.8",
    "141.86.21.76",
    "156.185.85.147",
    "75.199.165.137",
    "37.139.131.7",
    "54.12.162.209",
    "107.204.28.194",
    "175.21.132.112",
    "64.29.49.34",
    "34.24.230.140",
    "63.152.175.32",
    "112.239.127.143",
    "166.79.76.102",
    "49.148.17.1",
    "180.154.153.30",
    "61.173.17.3",
    "115.86.212.75",
    "195.6.124.188",
    "116.107.113.184",
    "74.159.149.140",
    "92.160.185.18",
    "53.111.119.119",
    "216.5.95.193",
    "31.194.50.198",
    "122.192.157.204",
    "150.8.129.205",
    "96.113.120.167",
    "34.201.183.248",
    "169.196.197.150",
    "94.78.27.104",
    "147.133.241.112",
    "137.231.251.221",
    "30.136.92.196",
    "171.156.20.218",
    "57.208.121.228",
    "214.0.95.59",
    "200.36.162.65",
    "89.209.29.120",
    "81.169.248.170",
    "206.134.22.124",
    "175.155.95.66",
    "137.247.18.17",
    "38.37.103.108",
]


class Event(BaseModel):
    acceptcharset: str = Field(default_factory=lambda: r.choice(["unknown"]))
    acceptencoding: str = Field(default_factory=lambda: r.choice(["deflate, gzip", "gzip, deflate, br", "gzip"]))
    acceptlanguage: str = Field(default_factory=lambda: r.choice(["en-GB,en-US;q=0.9,en;q=0.8", "unknown"]))
    browsername: str = Field(
        default_factory=lambda: fake.random_element(
            OrderedDict([("Chrome", 0.52), ("Firefox", 0.04), ("Safari", 0.31), ("Edge", 0.1)])
        )
    )
    browserversion: str = Field(default_factory=lambda: r.choice(["107.0", "107.0.0.0", "86.0.4240.80"]))
    cachecontrol: str = Field(default_factory=lambda: r.choice(["max-age=0", "unknown", "no-cache"]))
    city: str = Field(default_factory=lambda: fake.city())
    connection: str = Field(default_factory=lambda: r.choice(["Keep-Alive"]))
    contentlength: str = Field(default_factory=lambda: r.choice(["unknown"]))
    contenttype: str = Field(default_factory=lambda: r.choice(["unknown"]))
    country: str = Field(default_factory=lambda: fake.country_code())
    cpuarchitecture: str = Field(default_factory=lambda: r.choice(["unknown", "amd64"]))
    devicemodel: str = Field(default_factory=lambda: r.choice(["unknown"]))
    devicetype: str = Field(default_factory=lambda: r.choice(["unknown"]))
    devicevendor: str = Field(default_factory=lambda: r.choice(["unknown"]))
    enginename: str = Field(default_factory=lambda: r.choice(["Blink", "Gecko", "Trident"]))
    engineversion: str = Field(default_factory=lambda: r.choice(["107.0", "107.0.0.0", "86.0.4240.80"]))
    event_ts: datetime = Field(default_factory=lambda: datetime.utcnow())
    from_: str = Field(default_factory=lambda: r.choice(["unknown"]), alias="from")
    headers: str = Field(
        default_factory=lambda: r.choice(
            [
                "accept,accept-encoding,connection,host,user-agent,x-forwarded-for,x-forwarded-host,x-forwarded-proto,x-real-ip,x-vercel-edge-region,x-vercel-id,x-vercel-ip-city,x-vercel-ip-country,x-vercel-ip-country-region,x-vercel-ip-latitude,x-vercel-ip-longitude,x-vercel-ip-timezone,x-vercel-proxied-for",
                "accept,accept-encoding,accept-language,cache-control,connection,host,sec-ch-ua,sec-ch-ua-mobile,sec-ch-ua-platform,sec-fetch-dest,sec-fetch-mode,sec-fetch-site,sec-fetch-user,upgrade-insecure-requests,user-agent,x-forwarded-for,x-forwarded-host,x-forwarded-proto,x-real-ip,x-vercel-edge-region,x-vercel-id,x-vercel-ip-city,x-vercel-ip-country,x-vercel-ip-country-region,x-vercel-ip-latitude,x-vercel-ip-longitude,x-vercel-ip-timezone,x-vercel-proxied-for",
                "accept,accept-encoding,accept-language,connection,host,sec-ch-ua,sec-ch-ua-mobile,sec-ch-ua-platform,sec-fetch-dest,sec-fetch-mode,sec-fetch-site,sec-fetch-user,upgrade-insecure-requests,user-agent,x-forwarded-for,x-forwarded-host,x-forwarded-proto,x-real-ip,x-vercel-edge-region,x-vercel-id,x-vercel-ip-city,x-vercel-ip-country,x-vercel-ip-country-region,x-vercel-ip-latitude,x-vercel-ip-longitude,x-vercel-ip-timezone,x-vercel-proxied-for",
            ]
        )
    )
    host: str = Field(default_factory=lambda: r.choice(["https://logs.example.com"]))
    ip_address: str = Field(default_factory=lambda: r.choice(IP_LIST))
    is_bot: int = Field(default_factory=lambda: r.choice([0]))
    latitude: float = Field(default_factory=lambda: float(fake.latitude()))
    log_level: str = Field(
        default_factory=lambda: fake.random_element(OrderedDict([("INFO", 0.85), ("WARN", 0.13), ("ERROR", 0.02)]))
    )
    log_message: str = Field(default_factory=lambda: " ".join(fake.words(10)))
    longitude: float = Field(default_factory=lambda: float(fake.longitude()))
    method: str = Field(
        default_factory=lambda: fake.random_element(
            OrderedDict(
                [
                    ("GET", 0.6),
                    ("POST", 0.3),
                    ("DELETE", 0.1),
                    ("PUT", 0.1),
                    ("OPTIONS", 0.3),
                ]
            )
        )
    )
    origin: str = Field(default_factory=lambda: r.choice(["unknown"]))
    osname: str = Field(
        default_factory=lambda: fake.random_element(OrderedDict([("Windows", 0.6), ("Mac OS", 0.4), ("Linux", 0.1)]))
    )
    osversion: str = Field(default_factory=lambda: fake.numerify("%!!.%!!.%!!"))
    protocol: str = Field(default_factory=lambda: r.choice(["https"]))
    referer: str = Field(
        default_factory=lambda: r.choice(
            [
                "https://www.google.co.uk/",
                "https://www.bing.com/",
                "https://duckduckgo.com/",
                "https://yandex.com/",
                "https://yahoo.com",
            ]
        )
    )
    region: str = Field(default_factory=lambda: fake.country_code("alpha-3"))
    url: str = Field(
        default_factory=lambda: fake.random_element(
            OrderedDict(
                [
                    ("https://logs.example.com/api/v1/item", 0.6),
                    ("https://logs.example.com/api/v1/checkout", 0.2),
                    ("https://logs.example.com/api/v1/login", 0.1),
                    ("https://logs.example.com/api/v1/signup", 0.1),
                    ("https://logs.example.com/api/v1/fetch", 0.2),
                ]
            )
        )
    )
    useragent: str = Field(default_factory=lambda: fake.user_agent())
    via: str = Field(default_factory=lambda: r.choice(["unknown"]))
    xforwaredforip: str = Field(default_factory=lambda: r.choice(IP_LIST))


def generate() -> str:
    return Event().json(by_alias=True)
