import os

from werkzeug.wrappers import Response
from jinja2 import Environment, FileSystemLoader


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
