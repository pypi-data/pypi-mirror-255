class PackageService:

    __path = "/package"

    def __init__(self, http_client):
        self.http_client = http_client

    def get_path(self, *args):
        return "/".join([self.__path] + list(args))

    def fetch2(self, url, username, password):
        params = {"url": url, "user": username, "password": password}
        self.http_client.post(path=self.get_path("fetch2"), body=params)

    def get_importable_package(self):
        raise Exception('Not implemented.')

    def import_package(self):
        raise Exception('Not implemented.')

    def upload_package(self):
        raise Exception('Not implemented.')

    def fetch(self):
        raise Exception('Not implemented.')
