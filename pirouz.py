import inspect
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound, MethodNotAllowed


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
            if inspect.isclass(handler):
                method = request.method
                handler = getattr(handler(), method.lower(), None)
                if handler is None:
                    return self.method_not_exist(request, method, endpoint)
            return handler(request, **kwargs)
        except NotFound:
            return self.error_404(request)
        except MethodNotAllowed:
            return self.error_405(request)
        except HTTPException as error:
            return error

    def error_404(self, request):
        return TextResponse('Page Not Found', status=404)

    def error_405(self, request):
        return TextResponse(
            f'Method `{request.method}` is not allowed!',
            status=405,
        )

    def method_not_exist(self, request, method, view_name):
        return TextResponse(
            "Server Error:\n"
            f"The `{view_name}` view does not support"
            f" the `{method}` method.",
            status=500,
        )

    def check_route_exists(self, path, endpoint):
        if endpoint in self.routes:
            return True
        for rule in self.url_rules.iter_rules():
            if rule.rule == path:
                return True
        return False

    def route(self, path, methods=None):
        def wrapper(handler):
            endpoint = handler.__name__
            assert not self.check_route_exists(path, endpoint), (
                "Path already exists!"
            )
            rule = Rule(path, endpoint=endpoint, methods=methods)
            self.routes[endpoint] = handler
            self.url_rules.add(rule)
            return handler
        return wrapper
