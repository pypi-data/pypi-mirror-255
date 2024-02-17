import json
import mimetypes
import os
import sys
from dataclasses import dataclass, field

import MySQLdb
import requests
from termcolor import colored

from vulzap.db.sql import SQL
from vulzap.settings import VLogger

logger = VLogger(name="models", level="INFO")


@dataclass(unsafe_hash=True)
class Endpoint:
    url: str = ""
    method: str = ""
    resources: set = field(default_factory=set)

    @staticmethod
    def init() -> None:
        sql = SQL()

        query = "DROP TABLE IF EXISTS endpoint;"
        sql.execute(query=query, value=())

        query = "CREATE TABLE endpoint (`idx` INT AUTO_INCREMENT NOT NULL, `url` VARCHAR(100) NOT NULL, `method` VARCHAR(50) NOT NULL, `resource` VARCHAR(255) DEFAULT '', `sqli_done` BOOLEAN DEFAULT false, `xss_done` BOOLEAN DEFAULT false, PRIMARY KEY(`idx`), UNIQUE (`url`, `method`, `resource`));"
        sql.execute(query=query, value=())

    @staticmethod
    def plugin(plugin: str):
        result: list = []
        sql = SQL()

        if plugin not in ["xss", "sqli"]:
            logger.error(
                f"INVALID PLUGIN NAME: {plugin}",
                extra={"detail": "AVAILABLE PLUGIN: `xss`, `sqli`"},
            )
            sys.exit()

        query = f"""SELECT idx, url, method, resource FROM endpoint WHERE {plugin}_done = false;"""
        query_result = sql.select(query=query, value=())

        for q in query_result:
            result.append({"idx": q[0], "url": q[1], "method": q[2], "resource": q[3]})

        query = f"""UPDATE endpoint SET {plugin}_done = true;"""
        query_result = sql.execute(query=query, value=())

        return result

    @staticmethod
    def show() -> None:
        sql = SQL()

        query = f"""SELECT url, method, resource FROM endpoint;"""
        rows = sql.select(query=query, value=())

        if len(rows) == 0:
            print(colored("[-] NO DATA :(", "red"))
            return

        max_url_len = max(max(len(row[0]) for row in rows), 3)
        max_method_len = max(max([len(row[1]) for row in rows]), 6)
        max_resource_len = max(max([len(row[2]) for row in rows]), 8)

        print(
            colored(
                f"| {'URL':<{max_url_len}} | {'METHOD':<{max_method_len}} | {'RESOURCE':<{max_resource_len}} |",
                "green",
            )
        )

        for row in rows:
            url, method, resource = row

            if resource == "":
                resource = "-"

            print(
                colored(
                    f"| {url.ljust(max_url_len)} | {method.ljust(max_method_len)} | {resource.ljust(max_resource_len)} |",
                    "green",
                )
            )

        return

    @staticmethod
    def value() -> list:
        sql = SQL()
        query = f"""SELECT url, method, resource FROM endpoint;"""

        rows = sql.select(query=query, value=())

        return rows

    def save(self) -> None:
        sql = SQL()
        values: list = []

        if len(self.resources) == 0:
            value = (self.url, self.method, "")
            values.append(value)

        for resource in self.resources:
            value = (self.url, self.method, resource)
            values.append(value)

        query = f"""INSERT IGNORE INTO endpoint (url, method, resource) VALUES (%s, %s, %s);"""
        sql.executemany(query=query, values=values)


@dataclass(unsafe_hash=True)
class SqliReport:
    url: str
    is_vuln: bool
    payload: str = ""
    param: list = field(default_factory=list)
    data: list = field(default_factory=list)
    cve: str = ""

    @staticmethod
    def init() -> None:
        sql = SQL()
        query = "DROP TABLE IF EXISTS sqli_report;"
        sql.execute(query=query, value=())

        query = "CREATE TABLE sqli_report (`idx` INT AUTO_INCREMENT NOT NULL, `url` VARCHAR(100) NOT NULL, `is_vuln` BOOLEAN, `payload` VARCHAR(255), `param` VARCHAR(255), `data` VARCHAR(255), `cve` VARCHAR(30), PRIMARY KEY(`idx`));"
        sql.execute(query=query, value=())

    @staticmethod
    def show() -> None:
        sql = SQL()
        query = f"""SELECT url, payload, param, data FROM sqli_report;"""
        rows = sql.select(query=query, value=())

        if len(rows) == 0:
            print(colored("[-] NO DATA :(", "red"))
            return

        max_url_len = max(max(len(row[0]) for row in rows), 3)
        max_payload_len = max(max([len(row[1]) for row in rows]), 7)
        max_param_len = max(max([len(row[2]) for row in rows]), 5)
        max_data_len = max(max([len(row[3]) for row in rows]), 4)

        print(
            colored(
                f"| {'URL':<{max_url_len}} | {'PAYLOAD':<{max_payload_len}} | {'PARAM':<{max_param_len}} | {'DATA':<{max_data_len}} |",
                "green",
            )
        )

        for row in rows:
            url, payload, param, data = row

            if param == "":
                param = "-"

            if data == "":
                data = "-"

            print(
                colored(
                    f"| {url.ljust(max_url_len)} | {payload.ljust(max_payload_len)} | {param.ljust(max_param_len)} | {data.ljust(max_data_len)} |",
                    "green",
                )
            )

        return

    @staticmethod
    def value() -> tuple:
        sql = SQL()
        query = f"""SELECT * FROM sqli_report;"""
        return sql.select(query=query, value=())

    def save(self) -> None:
        sql = SQL()
        values: list = []

        if len(self.param) != 0:
            for p in self.param:
                value = (self.url, self.is_vuln, self.payload, p, "")
                values.append(value)

        if len(self.data) != 0:
            for d in self.data:
                value = (self.url, self.is_vuln, self.payload, "", d)
                values.append(value)

        query = f"""INSERT INTO sqli_report (url, is_vuln, payload, param, data, cve) VALUES (%s, %s, %s, %s, %s, "");"""

        sql.executemany(query=query, values=values)


@dataclass(unsafe_hash=True)
class XssReport:
    url: str
    is_vuln: bool
    payload: str = ""
    param: str = ""
    data: str = ""
    cve: str = ""

    @staticmethod
    def init() -> None:
        sql = SQL()
        query = "DROP TABLE IF EXISTS xss_report;"
        sql.execute(query=query, value=())

        query = "CREATE TABLE xss_report (`idx` INT AUTO_INCREMENT NOT NULL, `url` VARCHAR(100) NOT NULL, `is_vuln` BOOLEAN, `payload` VARCHAR(255), `param` VARCHAR(255), `data` VARCHAR(255), `cve` VARCHAR(30), PRIMARY KEY(`idx`));"
        sql.execute(query=query, value=())

    @staticmethod
    def show() -> None:
        sql = SQL()
        query = f"""SELECT url, payload, param, data FROM xss_report;"""
        rows = sql.select(query=query, value=())

        if len(rows) == 0:
            print(colored("[-] NO DATA :(", "red"))
            return

        max_url_len = max(max(len(row[0]) for row in rows), 3)
        max_payload_len = max(max([len(row[1]) for row in rows]), 7)
        max_param_len = max(max([len(row[2]) for row in rows]), 5)
        max_data_len = max(max([len(row[3]) for row in rows]), 4)

        print(
            colored(
                f"| {'URL':<{max_url_len}} | {'PAYLOAD':<{max_payload_len}} | {'PARAM':<{max_param_len}} | {'DATA':<{max_data_len}} |",
                "green",
            )
        )

        for row in rows:
            url, payload, param, data = row

            if param == "":
                param = "-"

            if data == "":
                data = "-"

            print(
                colored(
                    f"| {url.ljust(max_url_len)} | {payload.ljust(max_payload_len)} | {param.ljust(max_param_len)} | {data.ljust(max_data_len)} |",
                    "green",
                )
            )

        return

    @staticmethod
    def value() -> tuple:
        sql = SQL()
        query = f"""SELECT * FROM xss_report;"""
        return sql.select(query=query, value=())

    def save(self):
        sql = SQL()
        query = f"""INSERT INTO xss_report (url, is_vuln, payload, param, data, cve) VALUES (%s, %s, %s, %s, %s, %s);"""
        value = (self.url, self.is_vuln, self.payload, self.param, self.data, self.cve)

        sql.execute(query=query, value=value)


def initialize() -> None:
    Endpoint.init()
    SqliReport.init()
    XssReport.init()


if __name__ == "__main__":
    pass
