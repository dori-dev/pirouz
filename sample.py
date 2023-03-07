from pirouz import API, TextResponse

app = API()


@app.route('/')
def index(request):
    return TextResponse("Index Page.")


@app.route('/dashboard/')
def dashboard(request):
    return TextResponse("Dashboard Page")


@app.route('/user/<string:username>/')
def user(request, username):
    return TextResponse(f"Hello, {username}")
