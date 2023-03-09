import inspect
import os

from werkzeug.wrappers import Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound, MethodNotAllowed
from werkzeug.middleware.shared_data import SharedDataMiddleware
from jinja2 import Environment, FileSystemLoader

from middleware import BaseMiddleware


class TextResponse(Response):
    pass


class Render(Response):
    def __init__(
        self,
        template_name,
        template_dir="templates",
        context=None,
        **kwargs,
    ):
        if context is None:
            context = {}
        self.templates_env = Environment(
            loader=FileSystemLoader(os.path.abspath(template_dir))
        )
        text = self.templates_env.get_template(template_name).render(**context)
        super().__init__(text, content_type='text/html', **kwargs)


class App():
    ROOT_DIR = None
    config = {
        'debug': True,
        'reloader': True,
        'export_dirs': {
            '/static': 'static',
            '/media': 'media',
        },
    }

    def __init__(self, filename, production=False):
        self.routes = {}
        self.url_rules = Map()
        self.middleware = BaseMiddleware(self)
        self.set_config(filename, production)

    def set_config(self, filename, production):
        if self.ROOT_DIR is None:
            self.ROOT_DIR = os.path.dirname(filename)
        if production:
            self.config['debug'] = False

    def set_export_dirs(self, export_dirs: dict):
        export_dirs = export_dirs.copy()
        for url, dir in export_dirs.items():
            export_dirs[url] = os.path.join(self.ROOT_DIR, dir)
        self.config['export_dirs'] = export_dirs

    def __call__(self, environ, start_response):
        return self.middleware(environ, start_response)

    def add_middleware(self, middleware_cls):
        if isinstance(self.middleware, SharedDataMiddleware):
            raise Exception("You can't add middleware after serving files!")
        self.middleware.add(middleware_cls)

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

    def serve_files(self, use_defaults=True, export_dirs=None):
        if self.config['debug'] is False:
            raise Exception("You can't serve files in production mode!")
        if export_dirs is None:
            export_dirs = {}
        if use_defaults:
            export_dirs = self.config.get('export_dirs', {})
        self.set_export_dirs(export_dirs)
        self.middleware = SharedDataMiddleware(
            self.middleware,
            exports=self.config['export_dirs'],
        )
