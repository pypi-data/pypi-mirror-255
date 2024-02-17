import os
import sys
from ast import literal_eval
from dataclasses import dataclass, field
from urllib.parse import parse_qs, quote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from termcolor import colored

from vulzap.db import models
from vulzap.settings import VLogger
from vulzap.utils import is_blacklist, is_same_origin

logger = VLogger(name="crawl", level="INFO")

res = requests.get("https://vulzap.github.io/data/blacklist.json")
BLACKLIST: list = res.json().get("blacklist")


@dataclass
class Crawl:
    base: str = ""
    targets: set = field(default_factory=set)
    endpoints: list = field(default_factory=list)
    headless: bool = False
    depth: int = 0

    class Endpoint(models.Endpoint):
        pass

    def __post_init__(self):
        if self.headless:
            options = webdriver.ChromeOptions()
            for _ in [
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]:
                options.add_argument(_)

            self.driver = webdriver.Chrome(options=options)

    def encode(self, url: str) -> str:
        return quote(string=url, safe="?/:#&=", encoding="utf-8")

    def absolute(self, url: str) -> str:
        return urljoin(base=self.base, url=url)

    def str_to_dict(self, _str: str) -> dict:
        if _str == None or _str == "":
            return {}

        try:
            return literal_eval(_str)

        except Exception as e:
            logger.error("HEADER ERROR", extra={"detail": _str})
            return {}

    def remove_fragment(self, url: str) -> str:
        return urlparse(url=url)._replace(fragment="").geturl()

    def split_query(self, url: str) -> (str, set):
        param: set = set()

        for v in parse_qs(urlparse(url=url).query):
            param.add(v)

        url = url.replace("?" + urlparse(url=url).query, "")

        return url, param

    def request(self, url: str, header: dict) -> BeautifulSoup:
        """
        return 1: blacklist
        return 2: connection error
        return 3: unknown error
        """
        if is_blacklist(url=url):
            print("blacklisted", url)
            return 1

        if self.headless:
            try:
                self.driver.get(url=url)
                return BeautifulSoup(self.driver.page_source, "html.parser")

            except WebDriverException as e:
                logger.warning(
                    "SELENIUM WEBDRIVER ERROR", extra={"detail": f"{e.msg} | {url}"}
                )
                return 2

            except Exception as e:
                logger.error("UNKNOWN ERROR", extra={"detail": f"{e} | {url}"})
                sys.exit(0)

        else:
            try:
                response = requests.get(url=url, headers=header)
                return BeautifulSoup(response.text, "html.parser")

            except ConnectionError as e:
                logger.warning("CONNECTION FAILED", extra={"detail": url})
                return 2

            except Exception as e:
                logger.error("UNKNOWN ERROR", extra={"detail": f"{e} | {url}"})

    def find_href(self, soup: BeautifulSoup) -> set:
        """
        href 속성을 갖는 태그를 찾아 해당 URL 수집
        """
        result: set = set()

        for v in soup.find_all(name="a", href=True):
            url = self.remove_fragment(self.absolute(url=v["href"]))

            if is_same_origin(source=self.base, target=url) and not is_blacklist(
                url=url
            ):
                endpoint = self.Endpoint(method="GET")

                url, resources = self.split_query(url=url)
                endpoint.url = url
                endpoint.resources = resources

                self.endpoints.append(endpoint)
                result.add(url)

                logger.info("", extra={"detail": f"[GET] {url}"})

        return result

    def find_form(self, soup: BeautifulSoup) -> set:
        """
        form 태그를 찾아 URL / METHOD / RESOURCE 수집
        """
        result: set = set()

        for v in soup.find_all(name="form", action=True):
            endpoint = self.Endpoint()

            url = self.remove_fragment(self.absolute(url=v["action"]))

            if not is_same_origin(source=self.base, target=url) or is_blacklist(
                url=url
            ):
                continue

            method = v.get("method", "GET")

            for i in v.find_all(name="input"):
                name = i.get("name")

                if name != None:
                    if method.upper() == "GET":
                        endpoint.resources.add(name)
                    if method.upper() == "POST":
                        endpoint.resources.add(name)

                    endpoint.url = url
                    endpoint.method = method.upper()

            self.endpoints.append(endpoint)
            result.add(url)

            logger.info("", extra={"detail": f"[{method}] {url}"})

        return result

    def merge(self) -> None:
        result: dict = {}

        for u in self.endpoints:
            if u.url not in result:
                result[u.url] = u

            else:
                result[u.url].resources.update(u.resources)

        result_list = list(result.values())

        for x in result_list:
            x.save()

    def run(self, base: str, header: dict) -> None:
        self.base = base
        self.targets.add(base)

        header = self.str_to_dict(_str=header)

        visits: set = set()

        while len(self.targets) != 0:
            url = self.remove_fragment(self.targets.pop())

            if url not in visits:
                visits.add(url)

                soup = self.request(url=url, header=header)

                if soup == 1:
                    continue

                elif soup == 2:
                    logger.warning("REQUEST FAILED", extra={"detail": url})

                elif soup:
                    hrefs = self.find_href(soup=soup)
                    forms = self.find_form(soup=soup)

                    if hrefs:
                        self.targets.update(hrefs)

                    if forms:
                        self.targets.update(forms)

                else:
                    logger.error("UNKNOWN ERROR", extra={"detail": url})

        self.merge()


if __name__ == "__main__":
    crawl = Crawl(headless=False, depth=0)
    crawl.run(
        base="https://hanbyul.me",
        header="{}",
    )
