class Request:
    def __init__(self, url: str, service: str):
        self.url = url
        self.service = service
        self._response = None
        self._proxy = None

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        self._response = response

    @property
    def proxy(self):
        return self._proxy

    @proxy.setter
    def proxy(self, proxy):
        self._proxy = proxy
