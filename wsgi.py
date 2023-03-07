from webob import Request, Response


class API():
    def __init__(self):
        self.routes = {}

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request):
        for path, handler in self.routes.items():
            if path == request.path:
                response = handler(request)
                return response
        return self.raise404(request)

    def raise404(self, request):
        response = Response()
        response.text = "Page Not Found Error."
        response.status_code = 404
        return response

    def route(self, path):
        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper


app = API()


@app.route('/')
def index(request):
    response = Response()
    response.text = "Index Page."
    return response


@app.route('/dashboard/')
def dashboard(request):
    response = Response()
    response.text = "Dashboard Page."
    return response
