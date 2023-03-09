from pirouz import App, TextResponse, Render
from middleware import BaseMiddleware

app = App(__file__)


class MyMiddleware(BaseMiddleware):
    def process_request(self, request):
        print('Processing request', request.url)
        return request

    def process_response(self, request, response):
        print('Processing response', response)
        return response


class OtherMiddleware(BaseMiddleware):
    def process_request(self, request):
        print('Other middleware in request.')
        return request

    def process_response(self, request, response):
        print('Other middleware in response.')
        return response


app.add_middleware(MyMiddleware)
app.add_middleware(OtherMiddleware)
app.add_middleware(OtherMiddleware)

app.serve_files()


@app.route('/')
def index(request):
    context = {
        'id': 1,
        'users': ['Mohammad', 'Amir', 'Salar']
    }
    return Render('index.html', context=context, status=200)


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
