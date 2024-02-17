import asyncio

from mitmproxy import options
from mitmproxy.tools import dump

from vulzap.db.models import Endpoint
from vulzap.settings import VLogger
from vulzap.utils import is_blacklist, is_same_origin

logger = VLogger(name="proxy", level="INFO")


class Proxy:
    def __init__(self, host: str, port: int, target: str = None):
        self.host = host
        self.port = port
        self.target = target

    class ResponseLogger:
        def __init__(self, target: str = None):
            self.target = target

        def get_keys(self, q: tuple) -> set:
            _key: set = set()

            for v in q:
                _key.add(v[0])

            return _key

        def response(self, flow):
            url: str = flow.request.pretty_url.split("?", 1)[0]
            method: str = flow.request.method
            query: tuple = flow.request.query.fields

            if self.target is not None:
                source = self.target
            else:
                source = flow.request.pretty_url

            if not is_same_origin(source=source, target=url):
                return

            if is_blacklist(url=url):
                return

            endpoint = Endpoint(url=url, method=method)

            if len(query) != 0:
                endpoint.resources = self.get_keys(query)

            endpoint.save()

    async def main(self):
        opts = options.Options(listen_host=self.host, listen_port=self.port)

        master = dump.DumpMaster(
            opts,
            with_termlog=False,
            with_dumper=False,
        )
        master.addons.add(Proxy.ResponseLogger(target=self.target))

        logger.info(f"PROXY RUNNING -> {self.host}:{self.port} ...")

        await master.run()
        return
