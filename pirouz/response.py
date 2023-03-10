import os

from werkzeug.wrappers import Response
from werkzeug.routing import RequestRedirect
from jinja2 import Environment, FileSystemLoader


class TextResponse(Response):
    pass


class Render(Response):
    def __init__(
        self,
        request,
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
        context.update(self.get_context(request))
        text = self.templates_env.get_template(template_name).render(**context)
        super().__init__(text, content_type='text/html', **kwargs)

    def get_context(self, request) -> dict:
        return {}


def redirect(url: str) -> Response:
    response = RequestRedirect(url)
    return response.get_response()
