class ServiceManager:

    def __init__(self):

        self._services = []

    def register(self, service):

        self._services.append(service)

    def start_all(self):

        for service in self._services:

            service.start()

    def stop_all(self):

        for service in reversed(self._services):

            service.stop()
