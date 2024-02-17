import logging
import os
import platform
import sys
from dataclasses import dataclass

from dotenv import dotenv_values, load_dotenv
from termcolor import colored

pre_content = """DB_HOST={}
DB_PORT={}
DB_USER={}
DB_PASSWD={}
DB_NAME={}
"""


class VLogger:
    def __init__(self, name: str = "root", level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.get_level(level=level))

        if self.logger.handlers:
            return

        self.handler = logging.StreamHandler()

    def get_level(self, level: str):
        if level in ["INFO", "WARNING", "ERROR"]:
            return getattr(logging, level)
        else:
            raise ValueError("Invalid logging level")

    def info(self, msg, *args, **kwargs):
        log = colored("[I][%(asctime)s] %(message)s", "blue")

        if "extra" in kwargs:
            if "detail" in kwargs.get("extra"):
                log += colored("\n[*]%(detail)s\r", "blue")

        formatter = logging.Formatter(log)

        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        log = colored("[W][%(asctime)s] %(message)s", "light_red")

        if "extra" in kwargs:
            if "detail" in kwargs.get("extra"):
                log += colored("\n[*]%(detail)s\r", "light_red")

        formatter = logging.Formatter(log)

        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        log = colored("[E][%(asctime)s] %(message)s", "red")

        if "extra" in kwargs:
            if "detail" in kwargs.get("extra"):
                log += colored("\n[*]%(detail)s\r", "red")

        formatter = logging.Formatter(log)

        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

        self.logger.error(msg, *args, **kwargs)


@dataclass
class Env:
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_USER: str = "root"
    DB_PASSWD: str = ""
    DB_NAME: str = "vulzap"
    path: str = None

    def __post_init__(self):
        pl = platform.system()

        if pl == "Windows":
            self.path = os.path.join(os.environ["USERPROFILE"], ".vzrc")

        elif pl == "Darwin" or pl == "Linux":
            self.path = os.path.join(os.environ["HOME"], ".vzrc")

        else:
            print("[-] Not supported OS")
            sys.exit()

        if not os.path.exists(self.path):
            self.save()

        load_dotenv(dotenv_path=self.path)
        self.load()

    def _print(self):
        print(colored(f"[*] DB_HOST       {self.DB_HOST}", "blue"))
        print(colored(f"[*] DB_PORT       {self.DB_PORT}", "blue"))
        print(colored(f"[*] DB_USER       {self.DB_USER}", "blue"))
        print(colored(f"[*] DB_PASSWD     {self.DB_PASSWD}", "blue"))
        print(colored(f"[*] DB_NAME       {self.DB_NAME}", "blue"))

    def load(self):
        self.DB_HOST = os.environ["DB_HOST"]
        self.DB_PORT = os.environ["DB_PORT"]
        self.DB_USER = os.environ["DB_USER"]
        self.DB_PASSWD = os.environ["DB_PASSWD"]
        self.DB_NAME = os.environ["DB_NAME"]

    def save(self):
        content = pre_content.format(
            self.DB_HOST,
            self.DB_PORT,
            self.DB_USER,
            self.DB_PASSWD,
            self.DB_NAME,
        )

        with open(self.path, "w") as f:
            f.write(content)
