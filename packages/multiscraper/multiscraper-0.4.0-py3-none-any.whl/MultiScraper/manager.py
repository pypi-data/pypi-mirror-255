import asyncio

from .type import Request, ServiceManager, ProxyManager


class Manager:
    def __init__(self, proxies: ProxyManager | None = None, services: ServiceManager | None = None):
        self.proxies = proxies if proxies else ProxyManager()
        self.services = services if services else ServiceManager()
        self.work = {}

    def __repr__(self):
        return f'proxies: {self.proxies}, ' \
               f'services: {self.services}'

    def _check_data(self):
        self.proxies.check_data()
        self.services.check_data()

    async def get_proxy(self, request: Request):
        while True:
            base_limit = 0
            res = None
            if not self.work:
                raise SystemError('manager not started')
            for proxy in self.work:
                limit = self.work[proxy].get(request.service)
                if limit is None:
                    raise ValueError(f'service "{request.service}" not found')
                if limit > base_limit:
                    base_limit = limit
                    res = proxy
            if base_limit > 0:
                self.work[res][request.service] -= 1
                request._proxy = res
                break
            else:
                await asyncio.sleep(0.1)

    def create_work(self):
        for proxy in self.proxies:
            self.work[proxy] = {service.name: service.rate_limit for service in self.services}

    async def updating_work(self):
        while True:
            await asyncio.sleep(1)
            self.create_work()

    async def run_manager(self):
        self._check_data()
        self.create_work()
        asyncio.create_task(self.updating_work())
