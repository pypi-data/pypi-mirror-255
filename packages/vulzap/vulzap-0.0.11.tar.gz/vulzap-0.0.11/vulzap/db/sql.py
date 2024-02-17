import os
import sys
import time

import MySQLdb
from MySQLdb._exceptions import OperationalError

from vulzap.settings import Env, VLogger

logger = VLogger(name="db", level="ERROR")


class SQL:
    def __init__(self):
        env = Env()

        self.database = self.connection(
            host=env.DB_HOST,
            port=env.DB_PORT,
            user=env.DB_USER,
            passwd=env.DB_PASSWD,
            db=env.DB_NAME,
        )

        if self.database == None:
            sys.exit(1)

    def __del__(self):
        if self.database != None:
            self.database.close()

    def connection(
        self, host: str, port: str, user: str, passwd: str, db: str
    ) -> MySQLdb.connect:
        try:
            _database = MySQLdb.connect(
                host=host,
                port=int(port),
                user=user,
                passwd=passwd,
                db=db,
                charset="utf8",
            )

            return _database

        except OperationalError as e:
            logger.error("DB CONNECTION FAILED", extra={"detail": e})
            return None

        except ValueError as e:
            logger.error("DB Connection Failed", extra={"detail": e})
            return None

        except Exception as e:
            logger.error("UNKNOWN DB ERROR", extra={"detail": e})
            return None

    def execute(self, query: str, value: tuple) -> None:
        cursor = self.database.cursor()
        cursor.execute(query, value)

        self.database.commit()

    def executemany(self, query: str, values: list) -> None:
        cursor = self.database.cursor()
        cursor.executemany(query, values)

        self.database.commit()

    def select(self, query: str, value: tuple) -> list:
        cursor = self.database.cursor()
        cursor.execute(query, value)

        return cursor.fetchall()


if __name__ == "__main__":
    sql = SQL()
