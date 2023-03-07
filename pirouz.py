from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound


class TextResponse(Response):
    pass


class API():
    def __init__(self):
        self.routes = {}
        self.url_rules = Map()

    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)

    def wsgi(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch(request)
        return response(environ, start_response)

    def dispatch(self, request):
        adapter = self.url_rules.bind_to_environ(request)
        try:
            endpoint, kwargs = adapter.match()
            handler = self.routes[endpoint]
            return handler(request, **kwargs)
        except NotFound:
            return self.error_404(request)
        except HTTPException as error:
            return error

    def error_404(self, request):
        return TextResponse('Page Not Found', status=404)

    def route(self, path):
        def wrapper(handler):
            endpoint = handler.__name__
            rule = Rule(path, endpoint=endpoint)
            self.routes[endpoint] = handler
            self.url_rules.add(rule)
            return handler
        return wrapper
