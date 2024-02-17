from dataclasses import dataclass


@dataclass
class Service:
    name: str
    rate_limit: int


class ServiceManager:
    def __init__(self, services: list[Service] | None = None):
        self._services = services if services else []

    def add(self, service: Service):
        self._services.append(service)

    def remove(self, service: Service):
        self._services.remove(service)

    def __repr__(self):
        return f'{self._services}'

    def __len__(self):
        return len(self._services)

    def __getitem__(self, index):
        return self._services[index]

    def __setitem__(self, index, value):
        self._services[index] = value

    def __delitem__(self, index):
        del self._services[index]

    def check_data(self):
        if not self._services:
            raise ValueError('Service not specified')
