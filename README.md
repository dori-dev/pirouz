# Pirouz Web Framework

A web framework built with Python.

## Install Pirouz

```
pip install pirouz
```

## Imports

```python
from pirouz import (
    App, BaseMiddleware,
    Render as Render_, TextResponse, redirect,
    DB, ResultConfig, columns, OR
)
from pirouz.utils import cleaned_data, encrypt
```

## Create App

```python
app = App(__file__)
```

## Run Web Server

For run web server using python:

```python
if __name__ == '__main__':
    app.run(port=8001)
```

Run server using gunicorn:

```
gunicorn -w 4 app:app --reload
```

## Create Models

```python
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
```

## Create Middleware

```python
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
```

## Serve Files

```python
app.serve_files()
```

## Add Context Processor

```python

class Render(Render_):
    def get_context(self, request) -> dict:
        return {
            'user': request.user,
            'posts_count': Post.all().count(),
        }

```

## Function View

```python
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
```

## Class View

A detail view

```python
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
```

A create view

```python
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

```

## Authentication

Register

```python
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

```

Login

```python
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

```

Logout

```python


@app.route('/exit/', methods=['GET'])
class Logout:
    def get(self, request):
        response = redirect('/')
        response.delete_cookie('username')
        response.delete_cookie('password')
        return response

```

## Search View

```python
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

```

#

# Links

Download Source Code: [Click Here](https://github.com/dori-dev/pirouz/archive/refs/heads/main.zip)

My Github Account: [Click Here](https://github.com/dori-dev/)
