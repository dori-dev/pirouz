from werkzeug.wrappers import Request


class BaseMiddleware:
    def __init__(self, app):
        self.app: BaseMiddleware = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.app.dispatch(request)
        return response(environ, start_response)

    def add(self, middleware_cls):
        self.app = middleware_cls(self.app)

    def dispatch(self, request):
        request = self.process_request(request)
        response = self.app.dispatch(request)
        return self.process_response(request, response)

    def process_request(self, request):
        return request

    def process_response(self, request, response):
        return response
