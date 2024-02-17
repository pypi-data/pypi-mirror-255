import os
from urllib.parse import urlparse

import requests

res = requests.get("https://vulzap.github.io/data/blacklist.json")
BLACKLIST: list = res.json().get("blacklist")


def is_same_origin(source: str, target: str) -> bool:
    source_domain = ".".join(urlparse(url=source).netloc.split(".")[-2:])
    target_domain = ".".join(urlparse(url=target).netloc.split(".")[-2:])

    return source_domain == target_domain


def is_blacklist(url: str) -> bool:
    ext = (os.path.splitext(url)[1])[1:]

    if ext in BLACKLIST:
        return True

    return False


if __name__ == "__main__":
    pass
