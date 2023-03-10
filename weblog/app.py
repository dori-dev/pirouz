from random import randint
from datetime import datetime

from pirouz import (
    App, BaseMiddleware,
    Render as Render_, TextResponse, redirect,
    DB, ResultConfig, columns, OR
)
from pirouz.utils import cleaned_data, encrypt

app = App(__file__)


class User(DB):
    username = columns.VarChar(unique=True, nullable=False)
    password = columns.Text(nullable=False)
    email = columns.Text()
    first_name = columns.VarChar()
    last_name = columns.VarChar()


class Post(DB):
    title = columns.Text(nullable=False)
    body = columns.Text()
    author = columns.ForeignKey(User)
    like_count = columns.SmallInt(default=0)
    created = columns.Date()


class AuthMiddleware(BaseMiddleware):
    def process_request(self, request):
        request.user = None
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        try:
            user = User.filter(username=username).first()
            if user.password == password:
                request.user = user
        except Exception:
            pass
        return request


app.add_middleware(AuthMiddleware)
app.serve_files()


class Render(Render_):
    def get_context(self, request) -> dict:
        return {
            'user': request.user,
            'posts_count': Post.all().count(),
        }


@app.route('/')
def index(request):
    context = {
        'posts': Post.all(
            config=ResultConfig(
                order_by='id',
                reverse=True,
            )
        ),
    }
    return Render(request, 'post/list.html', context=context)


@app.route("/login/", methods=["GET", "POST"])
class Login:
    def get(self, request):
        return Render(request, 'post/login.html')

    def post(self, request):
        cd = cleaned_data(request)
        password = encrypt(cd['password'])
        username = cd['username']
        try:
            user = User.filter(username=username).first()
            if user and user.password == password:
                response = redirect('/')
                response.set_cookie('username', username)
                response.set_cookie('password', password)
                return response
        except Exception:
            pass
        return Render(request, 'post/login.html', context={'wrong': True})


@app.route('/exit/', methods=['GET'])
class Logout:
    def get(self, request):
        response = redirect('/')
        response.delete_cookie('username')
        response.delete_cookie('password')
        return response


@app.route("/register/", methods=["GET", "POST"])
class Register:
    def get(self, request):
        return Render(request, 'post/register.html')

    def post(self, request):
        cd = cleaned_data(request)
        password = encrypt(cd['password'])
        username = cd['username']
        try:
            user = User.filter(username=username).first()
            if user:
                return Render(
                    request,
                    'post/register.html',
                    context={'exists': True}
                )
        except Exception:
            pass
        User(
            username=username,
            password=password,
            email=cd['email'],
            first_name=cd['first_name'],
            last_name=cd['last_name'],
        )
        response = redirect('/')
        response.set_cookie('username', username)
        response.set_cookie('password', password)
        return response


@app.route('/post/<int:id>/')
class PostDetail:
    def get(self, request, id):
        post = Post.filter(id=id).first()
        if not post:
            return TextResponse(f'Post with ID {id} not found!', status=404)
        context = {
            'post': post,
            'author': User.filter(id=post.author).first(),
        }
        return Render(request, 'post/detail.html', context=context)

    def post(self, request, id):
        return self.get(request, id)


@app.route("/create/", methods=["GET", "POST"])
class PostCreate:
    def get(self, request):
        if not request.user:
            return redirect('/login/')
        return Render(request, 'post/create.html')

    def post(self, request):
        if not request.user:
            return redirect('/login/')
        cd = cleaned_data(request)
        post = Post(
            title=cd["title"],
            body=cd['body'],
            author=request.user,
            like_count=randint(1, 100),
            created=str(datetime.now().date()),
        )
        return redirect(f'/post/{post.id}/')


@app.route('/search/')
class Search:
    def get(self, request):
        query = request.args.get('search')
        context = {
            'search': True,
        }
        if query:
            posts = Post.filter(
                OR(
                    title__like=f'%{query}%',
                    body__like=f'%{query}%',
                ),
                config=ResultConfig(
                    order_by='id',
                    reverse=True,
                )
            )
            context.update({
                'posts': posts,
            })
        return Render(request, 'post/list.html', context=context)

    def post(self, request):
        return self.get(request)


if __name__ == '__main__':
    app.run(port=8001)
