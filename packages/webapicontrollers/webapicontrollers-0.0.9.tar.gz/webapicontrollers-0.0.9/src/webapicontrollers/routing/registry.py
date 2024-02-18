class Registry:
    def __init__(self):
        self.routes = []

    def add_route(self, func, path, method):
        self.routes.append((func, path, method))

    def get_routes(self):
        return self.routes
