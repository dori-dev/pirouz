from requests import Session
import pytest
from wsgiadapter import WSGIAdapter

from pirouz import (
    App, TextResponse, Render, BaseMiddleware
)

BASE_URL = 'http://testserver'


@pytest.fixture
def app():
    return App(__file__)


@pytest.fixture
def client(app):
    session = Session()
    session.mount(
        prefix=BASE_URL,
        adapter=WSGIAdapter(app),
    )
    return session


def test_basic_route(app, client):
    @app.route('/home')
    def home(request):
        return TextResponse('Home Page.')


def test_client_can_send_requests(app, client):
    TEXT = 'Hi Iam Mohammad Dori'

    @app.route('/hey/')
    def hey(request):
        return TextResponse(TEXT)
    assert client.get(f"{BASE_URL}/hey").text == TEXT
    assert client.get(f"{BASE_URL}/hey/").text == TEXT


def test_page_with_parameter(app, client):
    @app.route('/user/<int:id>/')
    def user(request, id):
        return TextResponse(f'Hi user with ID {id}')
    assert client.get(f"{BASE_URL}/user/1").text == 'Hi user with ID 1'
    assert client.get(f"{BASE_URL}/user/2/").text == 'Hi user with ID 2'


def test_404_error_response(app, client):
    assert client.get(f"{BASE_URL}/somethings/").status_code == 404
