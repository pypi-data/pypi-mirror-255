import asyncio
import os
from argparse import ArgumentParser
from ast import literal_eval
from urllib.parse import urlparse

from vulzap.core.crawl import Crawl
from vulzap.core.proxy import Proxy
from vulzap.db.models import Endpoint, SqliReport, XssReport, initialize
from vulzap.plugins.sqli import Scan as sqli_plugin
from vulzap.plugins.xss import main as xss_plugin
from vulzap.settings import Env, VLogger
from vulzap.web.app import app

logger = VLogger(name="main", level="INFO")


def crawl_main(url: str, header: str, depth: int, headless: bool):
    crawl = Crawl(depth=depth, headless=headless)
    crawl.run(base=url, header=header)


def proxy_main(host: str, port: int, target: str = None):
    proxy = Proxy(host=host, port=int(port), target=target)
    asyncio.run(proxy.main())


def xss_main(url: str, method: str):
    xss_plugin(url=url, method=method)


def sqli_main(data: str):
    sqli = sqli_plugin()
    sqli.run(data=literal_eval(data))


def sqli_exploit_main():
    sqli = Endpoint.plugin("sqli")
    sqli_target: dict = {}
    for _ in sqli:
        tmp = []
        tmp.append(_.get("resource"))

        if _.get("method") == "GET":
            res = {"GET": tmp, "POST": []}
        else:
            res = {"GET": [], "POST": tmp}

        data = str({_.get("url"): res})
        sqli_main(data=data)


def xss_exploit_main():
    xss = Endpoint.plugin("xss")
    for _ in xss:
        url = f"{_.get('url')}?{_.get('resource')}"
        xss_main(url=url, method=_.get("method"))


def main():
    parser = ArgumentParser()
    env = Env()

    subparsers = parser.add_subparsers(dest="command")
    parser_printenv = subparsers.add_parser("printenv", help="Print env")
    parser_setenv = subparsers.add_parser("setenv", help="Set Env")
    parser_init = subparsers.add_parser("init", help="Init")
    parser_gui = subparsers.add_parser("gui", help="GUI")
    parser_proxy = subparsers.add_parser("proxy", help="Proxy")
    parser_crawl = subparsers.add_parser("crawl", help="Crawl")
    parser_show = subparsers.add_parser("show", help="Show")
    parser_exploit = subparsers.add_parser("exploit", help="Exploit")

    parser_setenv.add_argument("key", help="Key")
    parser_setenv.add_argument("value", help="Value")

    parser_proxy.add_argument("--host", help="Proxy Host", required=True)
    parser_proxy.add_argument("--port", help="Proxy Port", required=True)
    parser_proxy.add_argument("--target", help="Target URL")

    parser_crawl.add_argument("-u", "--url", help="Target URL", required=True)
    parser_crawl.add_argument("-H", "--header", help="Header")
    parser_crawl.add_argument(
        "--headless", help="Headless", action="store_true", default=False
    )
    parser_crawl.add_argument("--depth", help="Depth (0-2)", default=0)

    parser_show.add_argument("tb", help="Table Name")

    parser_exploit.add_argument("--mode", help="Exploit Mode", required=True)
    parser_exploit.add_argument("-u", "--url", help="Target URL")
    parser_exploit.add_argument("-d", "--data", help="Request Data")
    parser_exploit.add_argument("-m", "--method", help="HTTP Method")

    args = parser.parse_args()

    if args.command == "printenv":
        env._print()

    elif args.command == "setenv":
        if hasattr(env, args.key):
            setattr(env, args.key, args.value)
            env.save()

        else:
            logger.error(
                f"NOT SUPPORTED KEY: {args.key}",
                extra={
                    "detail": "AVAILABLE KEY: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWD`, `DB_NAME`"
                },
            )

    elif args.command == "init":
        initialize()

    elif args.command == "gui":
        app.run(host="0.0.0.0", port=9000)

    elif args.command == "proxy":
        asyncio.run(proxy_main(host=args.host, port=args.port, target=args.target))

    elif args.command == "crawl":
        crawl_main(
            url=args.url, header=args.header, depth=args.depth, headless=args.headless
        )

    elif args.command == "show":
        if args.tb == "endpoint":
            Endpoint.show()

        elif args.tb == "xss_report":
            XssReport.show()

        elif args.tb == "sqli_report":
            SqliReport.show()

        else:
            logger.error(
                f"NOT SUPPORTED TABLE NAME: {args.tb}",
                extra={
                    "detail": "AVAILABLE TABLE: `endpoint`, `xss_report`, `sqli_report`"
                },
            )

    elif args.command == "exploit":
        if args.mode == "xss":
            xss_main(url=args.url, method=args.method)

        elif args.mode == "sqli":
            sqli_main(data=args.data)

        elif args.mode == "all":
            sqli_exploit_main()
            xss_exploit_main()

        else:
            logger.error(
                f"NOT SUPPORTED MODE: {args.mode}",
                extra={"detail": "AVAILABLE MODE: `xss`, `sqli`, `all"},
            )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
