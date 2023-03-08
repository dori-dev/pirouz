from pirouz import API, TextResponse
from middleware import BaseMiddleware

app = API()


class MyMiddleware(BaseMiddleware):
    def process_request(self, request):
        print('Processing request', request.url)
        return request

    def process_response(self, request, response):
        print('Processing response', response)
        return response


app.add_middleware(MyMiddleware)


@app.route('/')
def index(request):
    return TextResponse("Index Page.")


@app.route("/detail/", methods=["GET", "POST"])
class DetailView():
    def get(self, request):
        return TextResponse("Detail view with GET method.")

    def post(self, request):
        return TextResponse("Detail view with POST method.")


@app.route('/dashboard/')
def dashboard(request):
    return TextResponse("Dashboard Page")


@app.route('/user/<string:username>/')
def user(request, username):
    return TextResponse(f"Hello, {username}")


@app.route('/movie/<int:id>/')
def movie(request, id):
    return TextResponse(f"Loading the movie with id {id}")
